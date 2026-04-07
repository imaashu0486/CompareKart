/// Price Comparison Tile Widget
/// Displays price info for individual product

import 'package:flutter/material.dart';
import '../models/product_model.dart';

class PriceTile extends StatelessWidget {
  final Product product;
  final double? lowestPrice;
  final VoidCallback? onTap;

  const PriceTile({
    Key? key,
    required this.product,
    this.lowestPrice,
    this.onTap,
  }) : super(key: key);

  @override
  Widget build(BuildContext context) {
    final isBestDeal = lowestPrice != null && product.price == lowestPrice;
    final savings = lowestPrice != null ? product.price - lowestPrice! : null;
    final discountPercent = savings != null && lowestPrice != null
        ? ((product.price - lowestPrice!) / product.price * 100).toStringAsFixed(1)
        : null;

    return GestureDetector(
      onTap: onTap,
      child: Container(
        margin: const EdgeInsets.symmetric(horizontal: 16, vertical: 6),
        padding: const EdgeInsets.all(12),
        decoration: BoxDecoration(
          border: Border.all(
            color: isBestDeal ? Colors.green : Colors.grey[300]!,
            width: isBestDeal ? 2 : 1,
          ),
          borderRadius: BorderRadius.circular(8),
          color: isBestDeal ? Colors.green[50] : Colors.white,
        ),
        child: Row(
          children: [
            // Platform Icon
            Container(
              padding: const EdgeInsets.all(8),
              decoration: BoxDecoration(
                color: Colors.grey[200],
                borderRadius: BorderRadius.circular(6),
              ),
              child: Text(
                product.platform[0].toUpperCase(),
                style: const TextStyle(
                  fontWeight: FontWeight.bold,
                  fontSize: 12,
                ),
              ),
            ),
            const SizedBox(width: 12),

            // Platform and Price Info
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    product.platform,
                    style: const TextStyle(
                      fontWeight: FontWeight.w600,
                      fontSize: 13,
                    ),
                  ),
                  const SizedBox(height: 2),
                  Row(
                    children: [
                      Text(
                        '₹${product.price.toStringAsFixed(2)}',
                        style: const TextStyle(
                          fontWeight: FontWeight.bold,
                          fontSize: 14,
                          color: Colors.green,
                        ),
                      ),
                      if (discountPercent != null && savings! > 0) ...[
                        const SizedBox(width: 8),
                        Container(
                          padding: const EdgeInsets.symmetric(
                            horizontal: 6,
                            vertical: 2,
                          ),
                          decoration: BoxDecoration(
                            color: Colors.amber[100],
                            borderRadius: BorderRadius.circular(4),
                          ),
                          child: Text(
                            '+₹${savings.toStringAsFixed(2)}',
                            style: TextStyle(
                              fontSize: 11,
                              fontWeight: FontWeight.bold,
                              color: Colors.amber[900],
                            ),
                          ),
                        ),
                      ],
                    ],
                  ),
                ],
              ),
            ),

            // Best Deal Badge or Open Button
            if (isBestDeal)
              Container(
                padding: const EdgeInsets.symmetric(
                  horizontal: 10,
                  vertical: 4,
                ),
                decoration: BoxDecoration(
                  color: Colors.green,
                  borderRadius: BorderRadius.circular(4),
                ),
                child: const Row(
                  mainAxisSize: MainAxisSize.min,
                  children: [
                    Icon(Icons.check_circle, color: Colors.white, size: 14),
                    SizedBox(width: 4),
                    Text(
                      'Best Deal',
                      style: TextStyle(
                        color: Colors.white,
                        fontSize: 10,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                  ],
                ),
              )
            else
              Icon(Icons.chevron_right, color: Colors.grey[400]),
          ],
        ),
      ),
    );
  }
}
