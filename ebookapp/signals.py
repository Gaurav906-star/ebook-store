import boto3
from django.dispatch import receiver
from django.db.models.signals import post_save,post_delete
from .models import Book



dynamodb = boto3.resource('dynamodb')
book_table = dynamodb.Table('Books_Stock')

@receiver(post_save,sender=Book)
def sync_book_stock_to_dynamodb(sender, instance, **kwargs):
  book_table.put_item(
    Item = {
       "book_id": instance.id,
       "stock": instance.stock
    }

  )
  print(f"Book stock details are synced in dynamodb ${instance.id}")


@receiver(post_delete,sender=Book)
def delete_books_stock_from_dynamodb(sender,instance,**kwargs):
  book_table.delete_item(
    Key= {
      "book_id": instance.id
    }
  )
  print(f"book stock details deleted from dyanmodb ${instance.id}")
