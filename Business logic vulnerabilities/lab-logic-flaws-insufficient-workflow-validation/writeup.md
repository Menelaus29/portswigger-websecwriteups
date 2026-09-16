## Metadata

- **Difficulty:** Practitioner
- **Category:** Business logic vulnerabilities
- **Lab URL:** [Lab: Insufficient workflow validation](https://portswigger.net/web-security/logic-flaws/examples/lab-logic-flaws-insufficient-workflow-validation)
- **Date Solved:** 15/9/2026
## Vulnerability Summary

The app does not enforce a strict sequence of events in the purchasing workflow. More specifically, it does not validate that `POST /cart/checkout` is made before `GET /cart/order-confirmation?order-confirmed=true`. Since the app lacks server-side state tracking, this allows an attacker to intercept the `GET /cart/order-confirmation?order-confirmed=true` of another item that they had sufficient to buy before, then use this request to buy an item for free without performing `POST /cart/checkout`.
## Reconnaissance

- Logging in with the credentials `wiener - peter`, we see that we have `$100.00` store credit, while the item we have to buy, `Lightweight "l33t" Leather Jacket`, costs `$1337.00`. This means we are not able to buy this item normally, as there are no observable way to legitimately increase our store credit or reduce the item's price (even through coupons).
The purchasing workflow of an item is as follows:
1. We click on "View details" of the item (`GET /product?productId=10`)
2. On the item's page (`/product?productId=10`), we add it to cart (`POST /cart`)
3. We go to cart (`GET /cart`) to place an order (`POST /cart/checkout`). This checkout request will result in a `303 See Other` HTTP Response, which:
	- If we have enough store credit to buy the item, results in a `GET /cart/order-confirmation?order-confirmed=true`. The item is bought successfully, and its price is deducted from our store credits.
	- Else, `GET /cart?err=INSUFFICIENT_FUNDS` is encountered. The request reads `Not enough store credit for this purchase`.
We may be able to manipulate this intended workflow to be able to purchase the target item.
## Exploitation Steps

1. Log into your account (`wiener - peter`).
2. Buy another item normally. Outside of the target item, you can buy any item because all of them has a lower price than our store credits. The goal is to intercept and capture the `GET /cart/order-confirmation?order-confirmed=true` request, which is the final request in the purchasing workflow of successfully buying an item.
3. Add the target item `Lightweight "l33t" Leather Jacket` to cart (`POST /cart` with request body `productId=1&redir=PRODUCT&quantity=1`) (you can also do so manually on the website). Proceed to `GET /cart`, but do **not** click "Place order" (`POST /cart/checkout`).
4. Right after `GET /cart` where the cart contains the target item, send the intercepted `GET /cart/order-confirmation?order-confirmed=true`. You should receive a `200 OK` HTTP Response that reads `Your order is on its way!`, indicating that the item was successfully purchased. Lab is solved.
## Payload Used

`GET /cart/order-confirmation?order-confirmed=true`
Since the app does not strictly enforce the intended sequence of events in the purchasing workflow, navigating to the confirmation endpoint right after `GET /cart` and skipping `POST /cart/checkout` triggers the backend function to finalize the order for whatever is currently in our session's cart, bypassing the payment deduction logic triggered by `/cart/checkout`.
## Root Cause

The app is vulnerable due to an absence of server-side state management restricting the purchasing workflow. Specifically, the backend logic responsible for executing an order (moving an item from the cart to purchased status) is statically bound to the `GET /cart/order-confirmation` endpoint. The server implicitly trusts the client's navigation sequence and fails to verify if the prerequisite state transitions (such as deducting funds or completing the payment calculation via `POST /cart/checkout`) have successfully occurred for the current session.
## Remediation

1. **Implement Server-Side State Management:** The app must track the user's progress through the checkout workflow using session variables (e.g., a session state object) or database records. 
2. **Validate State Transitions:** Before processing a request at any step, the server must verify that the session is in the correct prerequisite state. For example, before loading the `GET /cart/order-confirmation` page and finalizing the cart, the backend must verify a flag such as `session['payment_processed'] == True`.
3. **Decouple Order Execution from Endpoint Access:** The business logic that finalizes an order and clears the cart must be tied to the successful completion of the payment processing function, not the loading of a confirmation URL. Accessing the confirmation URL out of sequence should simply redirect the user back to their current valid state (e.g., the cart page).