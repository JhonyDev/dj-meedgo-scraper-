"""INITIATE TRANSACTION"""
import json

# import checksum generation utility
# You can get this utility from https://developer.paytm.com/docs/checksum/
import PaytmChecksum
import requests

paytmParams = dict()

paytmParams["body"] = {
    "requestType": "Payment",
    "mid": "KdrBel67166523599721",
    "websiteName": "meedgo.com",
    "orderId": "ORDERID_98765",
    "callbackUrl": "https://<callback URL to be used by merchant>",
    "txnAmount": {
        "value": "1.00",
        "currency": "INR",
    },
    "userInfo": {
        "custId": "CUST_001",
    },
}

# Generate checksum by parameters we have in body
# Find your Merchant Key in your Paytm Dashboard at https://dashboard.paytm.com/next/apikeys 
checksum = PaytmChecksum.generateSignature(json.dumps(paytmParams["body"]), "QdE9x0og5gT@IEwj")

paytmParams["head"] = {
    "signature": checksum
}

post_data = json.dumps(paytmParams)

# for Staging
url = "https://securegw-stage.paytm.in/theia/api/v1/initiateTransaction?mid=YOUR_MID_HERE&orderId=ORDERID_98765"

# for Production
# url = "https://securegw.paytm.in/theia/api/v1/initiateTransaction?mid=YOUR_MID_HERE&orderId=ORDERID_98765"
response = requests.post(url, data=post_data, headers={"Content-type": "application/json"}).json()
print(response)

"""INVOKE PAYMENT FROM FRONTENT"""
"""
< script
type = "application/javascript"
src = "{HOST}/merchantpgpui/checkoutjs/merchants/{MID}.js"
onload = "onScriptLoad();"
crossorigin = "anonymous" > < / script >
< script >
function
onScriptLoad()
{
    var
config = {
    "root": "",
    "flow": "DEFAULT",
    "data": {
                "orderId": "", / * update order id * /
                                                "token": "", / *update
token
value * /
"tokenType": "TXN_TOKEN",
"amount": "" / * update
amount * /
},
"handler": {
    "notifyMerchant": function(eventName, data){
        console.log("notifyMerchant handler function called");
console.log("eventName => ", eventName);
console.log("data => ", data);
}
}
};
if (window.Paytm & & window.Paytm.CheckoutJS){
window.Paytm.CheckoutJS.onLoad(function excecuteAfterCompleteLoad() {
// initialze configuration using init method
window.Paytm.CheckoutJS.init(config).then(function onSuccess() {
// after successfully updating configuration, invoke JS Checkout
window.Paytm.CheckoutJS.invoke();
}).catch(function onError(error){
console.log("error => ", error);
});
});
}
}
< / script >
"""

"""VERIFY PAYMENT"""
# import requests
# import json
#
# # import checksum generation utility
# # You can get this utility from https://developer.paytm.com/docs/checksum/
# import PaytmChecksum
#
# # initialize a dictionary
# paytmParams = dict()
#
# # body parameters
# paytmParams["body"] = {
#
#     # Find your MID in your Paytm Dashboard at https://dashboard.paytm.com/next/apikeys
#     "mid": "YOUR_MID_HERE",
#
#     # Enter your order id which needs to be check status for
#     "orderId": "YOUR_ORDER_ID",
# }
#
# # Generate checksum by parameters we have in body
# # Find your Merchant Key in your Paytm Dashboard at https://dashboard.paytm.com/next/apikeys
# checksum = PaytmChecksum.generateSignature(json.dumps(paytmParams["body"]), "YOUR_MERCHANT_KEY")
#
# # head parameters
# paytmParams["head"] = {
#
#     # put generated checksum value here
#     "signature": checksum
# }
#
# # prepare JSON string for request
# post_data = json.dumps(paytmParams)
#
# # for Staging
# url = "https://securegw-stage.paytm.in/v3/order/status"
#
# # for Production
# # url = "https://securegw.paytm.in/v3/order/status"
#
# response = requests.post(url, data=post_data, headers={"Content-type": "application/json"}).json()
