from azure.communication.sms import SmsClient

connection_str = "endpoint=https://meedgootp.communication.azure.com/;accesskey=/wfHtMuem3QTq0thcoEau6s1immiDv9OVXgmcI0WuUfBPtF3c2KhNRMklBsmoQsf07RQAgULgkLb1K1+qtRqBQ=="
sms_client = SmsClient.from_connection_string(connection_str)

sms_responses = sms_client.send(
    from_="<leased-phone-number>",
    to="+923345529803",
    message="Hello World via SMS",
    enable_delivery_report=True,  # optional property
    tag="custom-tag")  # optional property
try:
    sms_responses = sms_client.send(
        from_="<leased-phone-number>",
        to=["+923345529803"],
        message="Hello World via SMS")

    for sms_response in sms_responses:
        if (sms_response.successful):
            print("Message with message id {} was successful sent to {}"
                  .format(sms_response.message_id, sms_response.to))
        else:
            print("Message failed to send to {} with the status code {} and error: {}"
                  .format(sms_response.to, sms_response.http_status_code, sms_response.error_message))
except Exception as ex:
    print('Exception:')
    print(ex)
