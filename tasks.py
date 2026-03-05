from celery import shared_task
from datetime import datetime, timedelta, timezone
from models import db, ScheduledOrder, OrderStatus
from services.order_service import OrderService
from utils.logger import log_info, log_error


@shared_task(bind=True, max_retries=3)
def process_pending_orders(self):
    """Process all pending orders that are due for execution"""
    try:
        log_info("Starting order processing task")
        
        # Get all pending orders
        pending_orders, error = OrderService.get_pending_orders()
        
        if error:
            log_error(f"Error getting pending orders: {error}")
            raise Exception(error)
        
        processed_count = 0
        for order in pending_orders:
            try:
                _, error = OrderService.execute_order(order.id)
                if error:
                    log_error(f"Error executing order {order.id}: {error}")
                else:
                    processed_count += 1
                    log_info(f"Order {order.id} executed successfully")
            
            except Exception as e:
                log_error(f"Error processing order {order.id}: {str(e)}")
        
        log_info(f"Order processing completed: {processed_count} orders processed")
        return {'processed': processed_count}
    
    except Exception as exc:
        log_error(f"Order processing task failed: {str(exc)}")
        # Retry with exponential backoff
        self.retry(exc=exc, countdown=60)