from playwright.async_api import async_playwright
from datetime import datetime
import logging
import asyncio
from types import TracebackType
from typing import Optional, Type

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class FloridaBusinessCrawler:
    BASE_URL = "https://search.sunbiz.org/Inquiry/CorporationSearch/ByName"
    DOCUMENT_BASE_URL = "https://search.sunbiz.org"


    def __init__(self):
        self.playwright = None
        self.browser = None
        self.context = None
        self.page = None

    async def initialize(self):
        if not self.playwright:
            self.playwright = await async_playwright().start()
            self.browser = await self.playwright.chromium.launch(headless=True)
            self.context = await self.browser.new_context()
            self.page = await self.context.new_page()

    async def close(self):
        if self.context:
            await self.context.close()
        if self.browser:
            await self.browser.close()
        if self.playwright:
            await self.playwright.stop()

    def __enter__(self):
        raise TypeError("Use async with instead")

    def __exit__(self, exc_type, exc_val, exc_tb):
        raise TypeError("Use async with instead")

    async def __aenter__(self) -> "FloridaBusinessCrawler":
        await self.initialize()
        return self

    async def __aexit__(
        self,
        exc_type: Optional[Type[BaseException]],
        exc_val: Optional[BaseException],
        exc_tb: Optional[TracebackType],
    ) -> None:
        await self.close()

    def parse_date(self, date_str):
        if not date_str:
            return None
        try:
            return datetime.strptime(date_str.strip(), "%m/%d/%Y")
        except ValueError:
            return None

    async def search_business(self, business_name):
        try:
            await self.initialize()
            await self.page.goto(self.BASE_URL)
            await self.page.fill("#SearchTerm", business_name)
            # print("Filled search term")
            await self.page.click("input[type='submit'][value='Search Now']")
            # print("Clicked search button")  # Wait for
            await self.page.wait_for_selector("#search-results")
            # print("Waited for search results")

            # Get all search results
            results = []
            # Get all rows from the search results table
            rows = await self.page.query_selector_all("#search-results tbody tr")
            # print(f"Found {len(rows)} search results")
            
            # Store hrefs of active businesses only
            hrefs = []
            for row in rows[:5]:  # Still limit to first 5 results
                status = await row.query_selector("td:nth-child(3)")
                status_text = await status.text_content()
                if status_text.strip().lower() == "active":
                    link = await row.query_selector("a[title='Go to Detail Screen']")
                    if link:
                        href = await link.get_attribute('href')
                        absolute_url = f"https://search.sunbiz.org{href}"
                        hrefs.append(absolute_url)
            
            # print(f"Found {len(hrefs)} active businesses")
            
            # Now navigate to each href
            for href in hrefs:
                await self.page.goto(href)
                await self.page.wait_for_selector(".searchResultDetail")
                # print("Loaded business detail page")
                
                business_data = {
                    "name": await self.page.text_content(".detailSection.corporationName p:nth-child(2)"),
                    "filing_number": await self.page.text_content(
                        "label[for='Detail_DocumentId'] + span"
                    ),
                    "status": await self.page.text_content(
                        "label[for='Detail_Status'] + span"
                    ),
                    "filing_date": self.parse_date(
                        await self.page.text_content(
                            "label[for='Detail_FileDate'] + span"
                        )
                    ),
                    "state_of_formation": await self.page.text_content(
                        "label[for='Detail_EntityStateCountry'] + span"
                    ),
                    "principal_address": await self.page.text_content(
                        ".detailSection:has(span:first-child:has-text('Principal Address')) span:nth-child(2) div"
                    ),
                    "mailing_address": await self.page.text_content(
                        ".detailSection:has(span:first-child:has-text('Mailing Address')) span:nth-child(2) div"
                    ),
                    "registered_agent_name": await self.page.text_content(
                        ".detailSection:has(span:first-child:has-text('Registered Agent Name & Address')) span:nth-child(2)"
                    ),
                    "registered_agent_address": await self.page.text_content(
                        ".detailSection:has(span:first-child:has-text('Registered Agent Name & Address')) span:nth-child(3) div"
                    ),
                }
                # Get filing history
                filing_history = []
                # First find the section with Document Images
                doc_sections = await self.page.query_selector_all(".detailSection")
                for section in doc_sections:
                    title_text = await section.query_selector("span:first-child")
                    if title_text:
                        title_content = await title_text.text_content()
                        if "Document Images" in title_content:
                            history_rows = await section.query_selector_all("table tr")
                            for row in history_rows:
                                link_element = await row.query_selector("a")
                                if link_element:
                                    link_text = await link_element.text_content()
                                    if " -- " in link_text:
                                        date_str, filing_type = link_text.split(" -- ", 1)
                                        filing = {
                                            "filing_type": filing_type,
                                            "filing_date": self.parse_date(date_str),
                                            "document_url": f"{self.DOCUMENT_BASE_URL}{await link_element.get_attribute('href')}"
                                        }
                                        # print("Document URL: ", filing["document_url"])
                                        filing_history.append(filing)

                business_data["filing_history"] = filing_history

                results.append(business_data)
                # Navigate back to search results and perform search again
                await self.page.goto(self.BASE_URL)
                await self.page.fill("#SearchTerm", business_name)
                await self.page.click("input[type='submit'][value='Search Now']")
                await self.page.wait_for_selector("#search-results")
            
            # print(f"Results: {results}")
            return results

        except Exception as e:
            logger.error(f"Error during crawling: {str(e)}")
            return []
        finally:
            await self.close()
