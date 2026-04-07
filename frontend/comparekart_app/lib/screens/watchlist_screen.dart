import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:url_launcher/url_launcher.dart';
import '../providers/watchlist_provider.dart';
import '../widgets/product_card.dart';

class WatchlistScreen extends StatelessWidget {
  const WatchlistScreen({super.key});

  Future<void> _openUrl(String url) async {
    if (await canLaunchUrl(Uri.parse(url))) {
      await launchUrl(Uri.parse(url), mode: LaunchMode.externalApplication);
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Watchlist'),
        actions: [
          Consumer<WatchlistProvider>(
            builder: (context, provider, _) {
              if (provider.items.isEmpty) return const SizedBox.shrink();
              return IconButton(
                tooltip: 'Clear watchlist',
                onPressed: provider.clear,
                icon: const Icon(Icons.delete_sweep_rounded),
              );
            },
          ),
        ],
      ),
      body: Consumer<WatchlistProvider>(
        builder: (context, provider, _) {
          if (provider.items.isEmpty) {
            return Center(
              child: Column(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  Icon(Icons.bookmark_border_rounded, size: 64, color: Colors.grey[400]),
                  const SizedBox(height: 10),
                  const Text('Your watchlist is empty', style: TextStyle(fontSize: 16, fontWeight: FontWeight.w600)),
                  const SizedBox(height: 6),
                  Text('Save offers to track price drops', style: TextStyle(color: Colors.grey[600])),
                ],
              ),
            );
          }

          return ListView.builder(
            padding: const EdgeInsets.only(bottom: 16),
            itemCount: provider.items.length,
            itemBuilder: (context, index) {
              final product = provider.items[index];
              return ProductCard(
                product: product,
                onTap: () => _openUrl(product.productUrl),
                onUrlTap: () => _openUrl(product.productUrl),
                isInWatchlist: true,
                onWatchlistTap: () => provider.toggle(product),
              );
            },
          );
        },
      ),
    );
  }
}
