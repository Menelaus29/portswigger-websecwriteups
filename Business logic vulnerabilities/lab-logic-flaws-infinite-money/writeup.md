## Metadata

- **Difficulty:** Practitioner
- **Category:** Business logic vulnerabilities
- **Lab URL:** [Lab: Infinite money logic flaw](https://portswigger.net/web-security/logic-flaws/examples/lab-logic-flaws-infinite-money)
- **Date Solved:** 16/9/2026
## Vulnerability Summary

The app contains a business logic vulnerability in its item purchasing workflow. Specifically, an user can use a coupon for an infinite amount of times. This allows them to buy `Gift card` - an item that gives a code that gives the user `$10.00` in store credit with the original price of `$10.00` - for `$7.00`, leading to a net positive of `$3.00` after every time. When performed enough times, this process can give the user enough store credit to buy the target item and potentially, an infinite amount of store credit.
## Reconnaissance

Logging in with the credentials `wiener - peter`, the account is provided with `$100.00` in store credit. The target item `Lightweight "l33t" Leather Jacket`, costs `$1337.00`.
The purchasing workflow of an item is as follows:
1. We click on "View details" of the item (`GET /product?productId=10`)
2. On the item's page (`/product?productId=10`), we add it to cart (`POST /cart`)
3. We go to cart (`GET /cart`) to place an order (`POST /cart/checkout`). This checkout request will result in a `303 See Other` HTTP Response, which:
	- If we have enough store credit to buy the item, results in a `GET /cart/order-confirmation?order-confirmed=true`. The item is bought successfully, and its price is deducted from our store credits.
	- Else, `GET /cart?err=INSUFFICIENT_FUNDS` is encountered. The request reads `Not enough store credit for this purchase`.
	We can also, optionally, use coupon code (`POST /cart/coupon`) for price reduction.
Analysis of the app reveals the discount code `SIGNUP30`, delivered upon signing up for the app's newsletter, providing a `30%` discount on the base item price.
There's also a new item previously unseen, `Gift Card`, that costs `$10.00` in store credit. With the `SIGNUP30` code, we are able to buy this item for `$7.00`. Upon purchasing, it gives a gift card that, when entered in the `/my-account` endpoint (`POST /gift-card`), gives `$10.00`. By using the coupon, we get a net positive of `$3.00` in store credit every time we buy a `Gift Card`. Try performing the process again reveals that the `SIGNUP30` coupon code still works. This means that if we perform the process for enough times, we will have enough store credit to buy the `Lightweight "l33t" Leather Jacket`.
## Exploitation Steps

I did not know how to automate the process described above using Burp alone - refer to their solution: [Lab: Infinite money logic flaw](https://portswigger.net/web-security/logic-flaws/examples/lab-logic-flaws-infinite-money). I have tried to do it but somehow could not.
Refer to the [Python exploit script](exploit.py). The script is just the process described above, automated enough times for the account to have enough store credit to buy the `Lightweight "l33t" Leather Jacket`. After doing so, it buys the item and verify the lab completion status by making a `GET` request to the lab's domain and check for the `Congratulations, you solved the lab!` text in the response.
## Payload Used

[Python exploit script](exploit.py)
It does take a while for our store credit to be high enough to buy the `Lightweight "l33t" Leather Jacket`. Also, the script is quite fragile, as in very prone to errors. Just rerun it if it ever runs into an error.
## Root Cause

- The app fails to track the usage state of promotional codes per user. It does not update a backend database to flag the `SIGNUP30` coupon as "used" for a specific account, allowing infinite reuse.
- The app treats cash-equivalent items (gift cards) identical to standard merchandise. Applying a percentage-based discount to a cash-equivalent item creates an unintended arbitrage opportunity. Even if the coupon couldn't be used infinitely, the user still would have a free `$3.00` in store credit.
## Remediation

- Introduce a `user_coupons` linkage table in the database. When a coupon is successfully applied during checkout, mark the coupon as `used` or `inactive` for that specific `user_id`. Check this state prior to authorizing any cart discount.
- Modify the pricing logic to explicitly exclude cash-equivalent items (e.g., gift cards, wallet top-ups) from percentage-based promotional discounts.