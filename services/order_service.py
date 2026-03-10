from datetime import datetime, timedelta, timezone
from models import db, ScheduledOrder, OrderLog, OrderStatus, RecurrenceType
from utils.validators import validate_scheduled_order
from utils.helpers import calculate_next_execution_time, is_within_recurrence_window, MOCK_ITEMS
from utils.logger import log_info, log_error
from services.notification_service import NotificationService


class OrderService:
    """Service for managing scheduled orders"""
    
    @staticmethod
    def create_order(user_id, item_id, quantity, scheduled_time, recurrence_type=None, recurrence_end=None, recurrence_pattern=None):
        """Create a new scheduled order"""
        try:
            # Validate input
            order_data = {
                'itemId': item_id,
                'quantity': quantity,
                'scheduledTime': scheduled_time,
                'recurrenceType': recurrence_type,
                'recurrenceEnd': recurrence_end
            }
            
            is_valid, error_msg = validate_scheduled_order(order_data)
            if not is_valid:
                return None, error_msg
            
            # Check if item exists
            item = next((i for i in MOCK_ITEMS if i['id'] == item_id), None)
            if not item:
                return None, f"Item {item_id} not found"
            
            # Parse times - ensure UTC
            try:
                if 'T' in scheduled_time and 'Z' not in scheduled_time and '+' not in scheduled_time:
                    # Parse as naive and set to UTC
                    scheduled_dt = datetime.fromisoformat(scheduled_time).replace(tzinfo=timezone.utc)
                else:
                    # Parse as aware/ISO
                    scheduled_dt = datetime.fromisoformat(scheduled_time.replace('Z', '+00:00'))
                    if scheduled_dt.tzinfo is None:
                        scheduled_dt = scheduled_dt.replace(tzinfo=timezone.utc)
            except ValueError as e:
                log_error(f"Error parsing scheduled_time '{scheduled_time}': {str(e)}")
                return None, f"Invalid scheduled time format: {scheduled_time}"
            
            recurrence_end_dt = None
            if recurrence_end:
                try:
                    if 'T' in recurrence_end and 'Z' not in recurrence_end and '+' not in recurrence_end:
                        recurrence_end_dt = datetime.fromisoformat(recurrence_end).replace(tzinfo=timezone.utc)
                    else:
                        recurrence_end_dt = datetime.fromisoformat(recurrence_end.replace('Z', '+00:00'))
                        if recurrence_end_dt.tzinfo is None:
                            recurrence_end_dt = recurrence_end_dt.replace(tzinfo=timezone.utc)
                except ValueError as e:
                    log_error(f"Error parsing recurrence_end '{recurrence_end}': {str(e)}")
                    return None, f"Invalid recurrence end format: {recurrence_end}"
            
            # Create order
            order = ScheduledOrder(
                user_id=user_id,
                item_id=item_id,
                quantity=quantity,
                scheduled_time=scheduled_dt,
                recurrence_type=recurrence_type or RecurrenceType.ONCE.value,
                recurrence_pattern=recurrence_pattern,
                recurrence_end=recurrence_end_dt,
                status=OrderStatus.PENDING.value
            )
            
            db.session.add(order)
            db.session.commit()
            
            log_info(f"Order created: {order.id} for user {user_id}")
            return order, None
        
        except Exception as e:
            db.session.rollback()
            log_error(f"Error creating order: {str(e)}")
            return None, "Failed to create order"
    
    @staticmethod
    def get_order(order_id, user_id):
        """Get a specific order"""
        try:
            order = ScheduledOrder.query.filter_by(id=order_id, user_id=user_id).first()
            if not order:
                return None, "Order not found"
            return order, None
        except Exception as e:
            log_error(f"Error retrieving order: {str(e)}")
            return None, "Failed to retrieve order"
    
    @staticmethod
    def get_user_orders(user_id):
        """Get all orders for a user"""
        try:
            orders = ScheduledOrder.query.filter_by(user_id=user_id).all()
            return orders, None
        except Exception as e:
            log_error(f"Error retrieving orders: {str(e)}")
            return None, "Failed to retrieve orders"
    
    @staticmethod
    def update_order(order_id, user_id, update_data):
        try:
            order = ScheduledOrder.query.filter_by(id=order_id, user_id=user_id).first()
            if not order:
                return None, "Order not found"
            
            if order.status != OrderStatus.PENDING.value:
                return None, "Only pending orders can be updated"
            
            # Update allowed fields
            if 'quantity' in update_data:
                order.quantity = update_data['quantity']
            
            scheduled_time = update_data.get('scheduledTime') or update_data.get('scheduled_time')
            if scheduled_time:
                try:
                    if 'T' in scheduled_time and 'Z' not in scheduled_time and '+' not in scheduled_time:
                        dt = datetime.fromisoformat(scheduled_time).replace(tzinfo=timezone.utc)
                    else:
                        dt = datetime.fromisoformat(scheduled_time.replace('Z', '+00:00'))
                        if dt.tzinfo is None:
                            dt = dt.replace(tzinfo=timezone.utc)
                    order.scheduled_time = dt
                except ValueError as e:
                    return None, f"Invalid scheduled time: {e}"
            
            # Handle recurrenceType
            if 'recurrenceType' in update_data or 'recurrence_type' in update_data:
                order.recurrence_type = update_data.get('recurrenceType') or update_data.get('recurrence_type')
            
            # Handle recurrencePattern
            if 'recurrencePattern' in update_data or 'recurrence_pattern' in update_data:
                order.recurrence_pattern = update_data.get('recurrencePattern') or update_data.get('recurrence_pattern')
            
            # Handle recurrenceEnd
            recurrence_end = update_data.get('recurrenceEnd') or update_data.get('recurrence_end')
            if recurrence_end:
                try:
                    if 'T' in recurrence_end and 'Z' not in recurrence_end and '+' not in recurrence_end:
                        dt_end = datetime.fromisoformat(recurrence_end).replace(tzinfo=timezone.utc)
                    else:
                        dt_end = datetime.fromisoformat(recurrence_end.replace('Z', '+00:00'))
                        if dt_end.tzinfo is None:
                            dt_end = dt_end.replace(tzinfo=timezone.utc)
                    order.recurrence_end = dt_end
                except ValueError:
                    return None, "Invalid recurrence end time"
            elif ('recurrenceEnd' in update_data or 'recurrence_end' in update_data) and recurrence_end is None:
                order.recurrence_end = None
            
            if 'status' in update_data:
                order.status = update_data['status']
            
            db.session.commit()
            log_info(f"Order updated: {order_id}")
            return order, None
        
        except Exception as e:
            db.session.rollback()
            log_error(f"Error updating order: {str(e)}")
            return None, "Failed to update order"
    
    @staticmethod
    def delete_order(order_id, user_id):
        try:
            order = ScheduledOrder.query.filter_by(id=order_id, user_id=user_id).first()
            if not order:
                return None, "Order not found"
            
            db.session.delete(order)
            db.session.commit()
            log_info(f"Order deleted: {order_id}")
            return True, None
        
        except Exception as e:
            db.session.rollback()
            log_error(f"Error deleting order: {str(e)}")
            return None, "Failed to delete order"
    
    @staticmethod
    def execute_order(order_id):
        """Execute an order and create log entry"""
        try:
            from utils.helpers import calculate_next_execution_time, is_within_recurrence_window, should_execute_order
            
            order = ScheduledOrder.query.get(order_id)
            if not order:
                return None, "Order not found"
            
            # Check if this order should execute today based on pattern
            if not should_execute_order(order):
                log_info(f"Order {order_id} skipped - not scheduled for today")
                
                # Still need to schedule next execution
                if order.recurrence_type and order.recurrence_type != RecurrenceType.ONCE.value:
                    next_time = calculate_next_execution_time(
                        order.scheduled_time, 
                        order.recurrence_type,
                        order.recurrence_pattern
                    )
                    if is_within_recurrence_window(next_time, order.recurrence_end):
                        order.scheduled_time = next_time
                    else:
                        order.status = OrderStatus.COMPLETED.value
                        db.session.commit()
                
                return None, "Order not scheduled for today"
            
            # Get item details
            item = next((i for i in MOCK_ITEMS if i['id'] == order.item_id), None)
            if not item:
                return None, "Item not found"
            
            total_price = item['price'] * order.quantity        

            log_entry = OrderLog(
                order_id=order_id,
                user_id=order.user_id,
                item_id=order.item_id,
                quantity=order.quantity,
                status='SUCCESS',
                details={
                    'itemName': item['name'],
                    'quantity': order.quantity,
                    'pricePerUnit': item['price'],
                    'totalPrice': total_price
                }
            )
            
            # Update order status and next execution
            order.status = OrderStatus.PROCESSING.value
            
            # Schedule next execution if recurring
            if order.recurrence_type and order.recurrence_type != RecurrenceType.ONCE.value:
                next_time = calculate_next_execution_time(
                    order.scheduled_time, 
                    order.recurrence_type,
                    order.recurrence_pattern
                )
                if is_within_recurrence_window(next_time, order.recurrence_end):
                    order.scheduled_time = next_time
                    order.status = OrderStatus.PENDING.value  # Reset to PENDING for next run
                else:
                    order.status = OrderStatus.COMPLETED.value
            else:
                order.status = OrderStatus.COMPLETED.value
            
            db.session.add(log_entry)
            db.session.commit()
            
            # Send notification
            NotificationService.send_notification(
                email=order.user.email,
                subject=f"Order {order_id} Executed",
                message=f"Your order for {item['name']} has been placed successfully.\nTotal: ${total_price:.2f}"
            )
            
            log_info(f"Order executed: {order_id}")
            return log_entry, None
        
        except Exception as e:
            db.session.rollback()
            log_error(f"Error executing order: {str(e)}")
            return None, "Failed to execute order"
    
    @staticmethod
    def get_pending_orders():
        try:
            now = datetime.now(timezone.utc)
            log_info(f"Checking for pending orders at {now}")
            
            pending_orders = ScheduledOrder.query.filter(
                ScheduledOrder.status == OrderStatus.PENDING.value
            ).all()
            
            log_info(f"Found {len(pending_orders)} pending orders total")
            
            # Filter by scheduled time
            due_orders = []
            for order in pending_orders:
                st = order.scheduled_time
                if st and st.tzinfo is None:
                    st = st.replace(tzinfo=timezone.utc)
                
                if st <= now:
                    due_orders.append(order)
            
            log_info(f"Found {len(due_orders)} orders due for execution")
            for order in due_orders:
                log_info(f"  - Order {order.id}: scheduled={order.scheduled_time}, now={now}")
            
            return due_orders, None
        except Exception as e:
            log_error(f"Error retrieving pending orders: {str(e)}")
            return None, "Failed to retrieve pending orders"
