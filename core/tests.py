import asyncio
from time import sleep

from pyppeteer import launch


async def scrape_website():
    # Launch the browser
    browser = await launch()

    # Create a new browser page
    page = await browser.newPage()

    # Navigate to the webpage
    await page.setJavaScriptEnabled(True)
    await page.goto('https://healthplus.flipkart.com/')
    await page.evaluate('window.scrollTo(0, document.body.scrollHeight)')

    # Extract data from the webpage here
    # You can use various methods provided by Pyppeteer to locate elements

    # Example: Extracting text from an element with a specific selector
    print(page)
    print(page.url)
    html = await page.content()
    print(html)
    sleep(100)
    # Close the browser
    await browser.close()


# Run the scraping function
asyncio.get_event_loop().run_until_complete(scrape_website())
