
import requests

LAMBDA_API = 'https://bz5cga6tkc.execute-api.us-east-1.amazonaws.com/prod/api/checkforquantity' 

def check_quantity_in_stock(book_id,requested_quantity):
  print('processing quantity')
  try:
    body = {"book_id": book_id, "requested_quantity": requested_quantity}
    response = requests.post(
        LAMBDA_API,
        json=body,
        timeout = 5
    )
    response.raise_for_status()
    print(f'quantity processing successful {response.json()}')
    return response.json()
    
  except requests.exceptions.Timeout as e:
      return {"error": "lambda function is timeout {e}"}
  except requests.exceptions.HTTPError as e:
      return {"error":"error in calling https request {e}"}
  except Exception as e :
      return {"error":str(e)}
    