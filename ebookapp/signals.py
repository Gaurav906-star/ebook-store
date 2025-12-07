import boto3
from django.dispatch import receiver
from django.db.models.signals import post_save,post_delete
from .models import Book





@receiver(post_save,sender=Book)
# pylint: disable=unused-argument
def sync_book_stock_to_dynamodb(sender, instance, **kwargs):
  """
  function will recieve the signal when post_save called on Mysql
  will sync the dynamodb on save operation
  """
  dynamodb = boto3.resource('dynamodb')
  book_table = dynamodb.Table('Books_Stock')
  book_table.put_item(
    Item = {
       "book_id": instance.id,
       "stock": instance.stock
    }

  )
  print(f"Book stock details are synced in dynamodb ${instance.id}")


@receiver(post_delete,sender=Book)
# pylint: disable=unused-argument
def delete_books_stock_from_dynamodb(sender,instance,**kwargs):
  """
  function will recieve the delete signal on any book entry delete
  will remove the stock entry from dynamodb
  """
  dynamodb = boto3.resource('dynamodb')
  book_table = dynamodb.Table('Books_Stock')
  book_table.delete_item(
    Key= {
      "book_id": instance.id
    }
  )
  print(f"book stock details deleted from dyanmodb ${instance.id}")
