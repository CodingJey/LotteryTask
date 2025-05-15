import argparse
import requests

def py_curl(url, method='GET', headers=None, data=None):
    """
    Makes an HTTP request to the specified URL, similar to curl.

    Args:
        url (str): The URL to request.
        method (str, optional): The HTTP method to use (e.g., 'GET', 'POST').
                                Defaults to 'GET'.
        headers (dict, optional): A dictionary of HTTP headers to send.
                                  Defaults to None.
        data (dict or str, optional): Data to send in the request body (for POST, PUT, etc.).
                                       Defaults to None.

    Returns:
        None: Prints the response status code and content.
    """
    try:
        # Make the request based on the specified method
        if method.upper() == 'GET':
            response = requests.get(url, headers=headers, timeout=10)
        elif method.upper() == 'POST':
            response = requests.post(url, headers=headers, data=data, timeout=10)
        elif method.upper() == 'PUT':
            response = requests.put(url, headers=headers, data=data, timeout=10)
        elif method.upper() == 'DELETE':
            response = requests.delete(url, headers=headers, timeout=10)
        elif method.upper() == 'HEAD':
            response = requests.head(url, headers=headers, timeout=10)
        elif method.upper() == 'OPTIONS':
            response = requests.options(url, headers=headers, timeout=10)
        else:
            print(f"Error: Unsupported HTTP method '{method}'")
            return

        # Raise an exception for bad status codes (4xx or 5xx)
        response.raise_for_status()

        # Print status code
        print(f"Status Code: {response.status_code}")
        print("-" * 20)

        # Print response headers (optional, uncomment if needed)
        # print("Response Headers:")
        # for key, value in response.headers.items():
        #     print(f"  {key}: {value}")
        # print("-" * 20)

        # Print response content
        # For JSON responses, you might want to print response.json()
        # For text responses, response.text is usually what you want
        print("Response Content:")
        try:
            # Attempt to parse and print as JSON if content type suggests it
            if 'application/json' in response.headers.get('Content-Type', '').lower():
                print(response.json())
            else:
                print(response.text)
        except requests.exceptions.JSONDecodeError:
            # Fallback to printing raw text if JSON decoding fails
            print(response.text)

    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP error occurred: {http_err}")
        if hasattr(http_err, 'response') and http_err.response is not None:
            print(f"Status Code: {http_err.response.status_code}")
            print(f"Response Body: {http_err.response.text}")
    except requests.exceptions.ConnectionError as conn_err:
        print(f"Error Connecting: {conn_err}")
    except requests.exceptions.Timeout as timeout_err:
        print(f"Timeout Error: {timeout_err}")
    except requests.exceptions.RequestException as req_err:
        print(f"An unexpected error occurred: {req_err}")

if __name__ == "__main__":
    # --- Command-Line Argument Parsing ---
    parser = argparse.ArgumentParser(
        description="A simple Python utility to make HTTP requests, similar to curl."
    )
    parser.add_argument("url", help="The URL to make the request to.")
    parser.add_argument(
        "-X", "--method",
        default="GET",
        help="HTTP method to use (e.g., GET, POST, PUT, DELETE). Default is GET."
    )
    parser.add_argument(
        "-H", "--header",
        action="append",
        help="HTTP header to include in the request (e.g., 'Content-Type: application/json'). Can be used multiple times."
    )
    parser.add_argument(
        "-d", "--data",
        help="Data to send in the request body (for POST, PUT). For JSON, provide a string like '{\"key\":\"value\"}'."
    )

    args = parser.parse_args()

    # --- Prepare Headers ---
    # The 'header' argument will be a list of strings like ['Header1: Value1', 'Header2: Value2']
    # We need to convert this into a dictionary.
    request_headers = {}
    if args.header:
        for h in args.header:
            try:
                name, value = h.split(":", 1)
                request_headers[name.strip()] = value.strip()
            except ValueError:
                print(f"Warning: Ignoring malformed header: {h}. Headers should be in 'Name: Value' format.")

    # --- Call the Function ---
    py_curl(args.url, method=args.method, headers=request_headers, data=args.data)

