from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from services.order_service import OrderService
from utils.helpers import MOCK_ITEMS, format_execution_time
from utils.logger import log_info, log_error

orders_bp = Blueprint('orders', __name__, url_prefix='/api/orders')


@orders_bp.route('', methods=['GET'])
@jwt_required()
def get_orders():
    """Get all orders for the user"""
    try:
        user_id = get_jwt_identity()
        orders, error = OrderService.get_user_orders(user_id)
        
        if error:
            return jsonify({'error': error}), 500
        
        orders_data = []
        for order in orders:
            item = next((i for i in MOCK_ITEMS if i['id'] == order.item_id), None)
            orders_data.append({
                'id': order.id,
                'itemId': order.item_id,
                'itemName': item['name'] if item else 'Unknown',
                'quantity': order.quantity,
                'scheduledTime': format_execution_time(order.scheduled_time),
                'recurrenceType': order.recurrence_type,
                'recurrenceEnd': format_execution_time(order.recurrence_end) if order.recurrence_end else None,
                'status': order.status
            })
        
        return jsonify({'orders': orders_data}), 200
    
    except Exception as e:
        log_error(f"Error retrieving orders: {str(e)}")
        return jsonify({'error': 'Failed to retrieve orders'}), 500


@orders_bp.route('', methods=['POST'])
@jwt_required()
def create_order():
    """Create a new scheduled order"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        if not data or 'itemId' not in data or 'quantity' not in data or 'scheduledTime' not in data:
            return jsonify({'error': 'itemId, quantity, and scheduledTime are required'}), 400
        
        order, error = OrderService.create_order(
            user_id=user_id,
            item_id=data['itemId'],
            quantity=data['quantity'],
            scheduled_time=data['scheduledTime'],
            recurrence_type=data.get('recurrenceType'),
            recurrence_end=data.get('recurrenceEnd')
        )
        
        if error:
            return jsonify({'error': error}), 400
        
        item = next((i for i in MOCK_ITEMS if i['id'] == order.item_id), None)
        
        return jsonify({
            'message': 'Order created successfully',
            'order': {
                'id': order.id,
                'itemId': order.item_id,
                'itemName': item['name'] if item else 'Unknown',
                'quantity': order.quantity,
                'scheduledTime': format_execution_time(order.scheduled_time),
                'status': order.status
            }
        }), 201
    
    except Exception as e:
        log_error(f"Error creating order: {str(e)}")
        return jsonify({'error': 'Failed to create order'}), 500


@orders_bp.route('/<order_id>', methods=['GET'])
@jwt_required()
def get_order(order_id):
    """Get a specific order"""
    try:
        user_id = get_jwt_identity()
        order, error = OrderService.get_order(order_id, user_id)
        
        if error:
            return jsonify({'error': error}), 404
        
        item = next((i for i in MOCK_ITEMS if i['id'] == order.item_id), None)
        
        return jsonify({
            'order': {
                'id': order.id,
                'itemId': order.item_id,
                'itemName': item['name'] if item else 'Unknown',
                'quantity': order.quantity,
                'scheduledTime': format_execution_time(order.scheduled_time),
                'recurrenceType': order.recurrence_type,
                'recurrenceEnd': format_execution_time(order.recurrence_end) if order.recurrence_end else None,
                'status': order.status,
                'createdAt': format_execution_time(order.created_at)
            }
        }), 200
    
    except Exception as e:
        log_error(f"Error retrieving order: {str(e)}")
        return jsonify({'error': 'Failed to retrieve order'}), 500


@orders_bp.route('/<order_id>', methods=['PUT'])
@jwt_required()
def update_order(order_id):
    """Update an order"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        order, error = OrderService.update_order(order_id, user_id, data)
        
        if error:
            return jsonify({'error': error}), 400
        
        item = next((i for i in MOCK_ITEMS if i['id'] == order.item_id), None)
        
        return jsonify({
            'message': 'Order updated successfully',
            'order': {
                'id': order.id,
                'itemId': order.item_id,
                'itemName': item['name'] if item else 'Unknown',
                'quantity': order.quantity,
                'scheduledTime': format_execution_time(order.scheduled_time),
                'status': order.status
            }
        }), 200
    
    except Exception as e:
        log_error(f"Error updating order: {str(e)}")
        return jsonify({'error': 'Failed to update order'}), 500


@orders_bp.route('/<order_id>', methods=['DELETE'])
@jwt_required()
def delete_order(order_id):
    """Delete an order"""
    try:
        user_id = get_jwt_identity()
        _, error = OrderService.delete_order(order_id, user_id)
        
        if error:
            return jsonify({'error': error}), 400
        
        return jsonify({'message': 'Order deleted successfully'}), 200
    
    except Exception as e:
        log_error(f"Error deleting order: {str(e)}")
        return jsonify({'error': 'Failed to delete order'}), 500


@orders_bp.route('/items', methods=['GET'])
@jwt_required()
def get_items():
    """Get available items for ordering"""
    try:
        items = [{
            'id': item['id'],
            'name': item['name'],
            'price': item['price']
        } for item in MOCK_ITEMS]
        
        return jsonify({'items': items}), 200
    
    except Exception as e:
        log_error(f"Error retrieving items: {str(e)}")
        return jsonify({'error': 'Failed to retrieve items'}), 500
