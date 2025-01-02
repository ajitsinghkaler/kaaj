from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List
import logging

from ..database.connection import get_db, init_db
from ..models.business import Business  , FilingHistory
from ..crawler.florida_crawler import FloridaBusinessCrawler
from sqlalchemy.orm import joinedload


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Florida Business Search API")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup_event():
    init_db()


@app.get("/")
async def root():
    return {"message": "Florida Business Search API"}


@app.get("/search/{business_name}")
async def search_business(business_name: str, db: Session = Depends(get_db)):
    try:
        # Check if we already have the business in our database
        existing_business = (
            db.query(Business).options(joinedload(Business.filing_history)).filter(Business.name.ilike(f"%{business_name}%")).first()
        )

        if existing_business:
            return {
                "source": "database",
                "data": existing_business,
            }

        # If not in database, crawl the website
        async with FloridaBusinessCrawler() as crawler:
            results = await crawler.search_business(business_name)

            logger.info(f"Crawler results type: {type(results)}, value: {results}")
            if results is None:  # More specific check
                logger.info("No results found from crawler")
                return {
                    "source": "crawler",
                    "data": [],  # Return empty list instead of 404
                }

            # Store results in database
            stored_businesses = []
            for result in results:
                business = Business(
                    name=result["name"],
                    filing_number=result["filing_number"],
                    status=result["status"],
                    filing_date=result["filing_date"],
                    state_of_formation=result["state_of_formation"],
                    principal_address=result["principal_address"],
                    mailing_address=result["mailing_address"],
                    registered_agent_name=result["registered_agent_name"],
                    registered_agent_address=result["registered_agent_address"],
                )
                
                db.add(business)
                db.flush()  # Get the business ID

                # Add filing history
                for filing_data in result["filing_history"]:
                    filing = FilingHistory(
                        business_id=business.id,
                        filing_type=filing_data["filing_type"],
                        filing_date=filing_data["filing_date"],
                        document_url=filing_data["document_url"]
                    )
                    db.add(filing)

                stored_businesses.append(business)

            db.commit()
            return {"source": "crawler", "data": results}

    except Exception as e:
        logger.error(f"Error during search: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/business/{business_id}")
async def get_business(business_id: int, db: Session = Depends(get_db)):
    business = db.query(Business).filter(Business.id == business_id).first()
    if not business:
        raise HTTPException(status_code=404, detail="Business not found")

    return {
        "business": business,
    }
