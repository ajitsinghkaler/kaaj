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
            await self.page.click("input[type='submit'][value='Search Now']")
            await self.page.wait_for_selector("#search-results")

            # Get all search results
            results = []
            links = await self.page.query_selector_all("a[title='Go to Detail Screen']")

            for link in links[:5]:  # Limit to first 5 results
                await link.click()
                await self.page.wait_for_selector(".searchResultDetail")

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
                        ".detailSection span:first-child:has-text('Principal Address') + span div"
                    ),
                    "mailing_address": await self.page.text_content(
                        ".detailSection span:first-child:has-text('Mailing Address') + span div"
                    ),
                    "registered_agent_name": await self.page.text_content(
                        ".detailSection span:first-child:has-text('Registered Agent Name') + span"
                    ),
                    "registered_agent_address": await self.page.text_content(
                        ".detailSection span:first-child:has-text('Registered Agent Name') ~ span div"
                    ),
                }

                # Get officers
                officers = []
                # First find the section with Officer/Director Detail
                officer_sections = await self.page.query_selector_all(".detailSection")
                for section in officer_sections:
                    title_text = await section.query_selector("span:first-child")
                    if title_text and "Officer/Director Detail" in await title_text.text_content():
                        # Get all text content and process it
                        section_content = await section.text_content()
                        # Split by "Title" to get officer blocks
                        officer_blocks = section_content.split("Title")
                        
                        for block in officer_blocks[1:]:  # Skip the header block
                            lines = [line.strip() for line in block.split('\n') if line.strip()]
                            if len(lines) >= 2:
                                title = lines[0].strip()  # First line is the title
                                # Find the name (it's usually after the title and before the address)
                                name = None
                                address_lines = []
                                for line in lines[1:]:
                                    if not name:
                                        name = line
                                    else:
                                        address_lines.append(line)
                                
                                if name:
                                    officer = {
                                        "name": name,
                                        "title": title,
                                        "address": "\n".join(address_lines)
                                    }
                                    officers.append(officer)

                business_data["officers"] = officers

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
                                            "document_url": await link_element.get_attribute("href")
                                        }
                                        filing_history.append(filing)

                business_data["filing_history"] = filing_history
                results.append(business_data)

                await self.page.go_back()

            return results

        except Exception as e:
            logger.error(f"Error during crawling: {str(e)}")
            return []
        finally:
            await self.close()
