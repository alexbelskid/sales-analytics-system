from typing import List, Dict, Any
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


def calculate_abc_classification(items: List[Dict[str, Any]], value_key: str = "revenue") -> List[Dict[str, Any]]:
    """
    ABC classification using Pareto principle (80/20 rule).
    
    A-items: Top 80% of value (typically ~20% of items)
    B-items: Next 15% of value (typically ~30% of items)
    C-items: Last 5% of value (typically ~50% of items)
    
    Args:
        items: List of dicts with at least {id, name, value_key}
        value_key: Key to use for value (default: "revenue")
    
    Returns:
        List of items with added "abc_class" field
    """
    if not items:
        return []
    
    # Sort by value descending
    sorted_items = sorted(items, key=lambda x: float(x.get(value_key, 0)), reverse=True)
    
    # Calculate total value
    total_value = sum(float(item.get(value_key, 0)) for item in sorted_items)
    
    if total_value == 0:
        # All items are C if no value
        for item in sorted_items:
            item["abc_class"] = "C"
        return sorted_items
    
    # Calculate cumulative percentage
    cumulative_value = 0
    for item in sorted_items:
        cumulative_value += float(item.get(value_key, 0))
        cumulative_pct = (cumulative_value / total_value) * 100
        
        if cumulative_pct <= 80:
            item["abc_class"] = "A"
        elif cumulative_pct <= 95:
            item["abc_class"] = "B"
        else:
            item["abc_class"] = "C"
        
        item["cumulative_pct"] = round(cumulative_pct, 2)
    
    return sorted_items


def calculate_xyz_classification(items: List[Dict[str, Any]], sales_history: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    XYZ classification based on demand variability (coefficient of variation).
    
    X-items: CV < 10% (stable demand)
    Y-items: 10% <= CV < 25% (moderate variability)
    Z-items: CV >= 25% (high variability)
    
    Args:
        items: List of items with product_id
        sales_history: List of sales records with {product_id, period, quantity}
    
    Returns:
        List of items with added "xyz_class" and "cv" fields
    """
    if not items or not sales_history:
        # Default to Z (unknown variability)
        for item in items:
            item["xyz_class"] = "Z"
            item["cv"] = 0
        return items
    
    # Group sales by product_id
    product_sales = {}
    for sale in sales_history:
        pid = sale.get("product_id")
        qty = float(sale.get("quantity", 0))
        
        if pid not in product_sales:
            product_sales[pid] = []
        product_sales[pid].append(qty)
    
    # Calculate CV for each product
    for item in items:
        pid = item.get("product_id") or item.get("id")
        sales = product_sales.get(pid, [])
        
        if len(sales) < 2:
            # Not enough data - classify as Z
            item["xyz_class"] = "Z"
            item["cv"] = 0
            continue
        
        # Calculate mean and std dev
        mean = sum(sales) / len(sales)
        variance = sum((x - mean) ** 2 for x in sales) / len(sales)
        std_dev = variance ** 0.5
        
        # Coefficient of Variation (CV) = (std_dev / mean) * 100
        cv = (std_dev / mean * 100) if mean > 0 else 0
        
        if cv < 10:
            item["xyz_class"] = "X"
        elif cv < 25:
            item["xyz_class"] = "Y"
        else:
            item["xyz_class"] = "Z"
        
        item["cv"] = round(cv, 2)
    
    return items


def combine_abc_xyz(items: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
    """
    Combine ABC and XYZ classifications into matrix.
    
    Returns:
        Dict with keys like "AX", "AY", "AZ", "BX", etc.
    """
    matrix = {
        "AX": [], "AY": [], "AZ": [],
        "BX": [], "BY": [], "BZ": [],
        "CX": [], "CY": [], "CZ": []
    }
    
    for item in items:
        abc = item.get("abc_class", "C")
        xyz = item.get("xyz_class", "Z")
        key = f"{abc}{xyz}"
        
        if key in matrix:
            matrix[key].append(item)
    
    return matrix
