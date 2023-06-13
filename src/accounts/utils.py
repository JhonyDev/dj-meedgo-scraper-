from core.settings import BASE_URL
def get_email_template(unique_id):
    style = """
    <style>
        body {
            font-family: Arial, sans-serif;
            background-color: #f2f2f2;
            margin: 0;
            padding: 0;
        }

        .container {
            max-width: 600px;
            margin: 0 auto;
            background-color: #fff;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0 2px 6px rgba(0, 0, 0, 0.1);
        }

        h1 {
            color: #333;
            text-align: center;
        }

        p {
            color: #666;
            font-size: 18px;
            line-height: 1.6;
            margin-bottom: 20px;
        }

        a {
            display: inline-block;
            background-color: #4CAF50;
            color: #fff;
            text-decoration: none;
            padding: 10px 20px;
            border-radius: 4px;
        }
    </style>"""
    return f"""
     <html>
<head>
    {style}
</head>
<body>
    <div class="container">
        <h1>Email Verification</h1>
        <p>Please click the link below to verify your email address:</p>
        <p><a href="{BASE_URL}/verify-email/{unique_id}/">Verify Email Address</a></p>
    </div>
</body>
</html>
"""
