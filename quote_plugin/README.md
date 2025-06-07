# Quote Bot

This is a sample [maubot](https://github.com/maubot/maubot) plugin that lets a seller send quotes to a buyer via Matrix direct messages without using commands. A simple HTML form is provided for creating a quote. The buyer receives a message with **Pay now** and **Decline** buttons.

## Usage
1. Install the plugin in a maubot instance.
2. Enable the plugin with web support so that the form is reachable.
3. Open the plugin web page `/new` and fill in buyer information and item details.
4. The bot will open a direct chat with the buyer and send the quote.
5. The buyer can click **Pay now** or **Decline** which calls back to the plugin and notifies the seller.
