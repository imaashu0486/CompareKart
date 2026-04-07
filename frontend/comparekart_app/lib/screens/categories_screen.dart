import 'package:flutter/material.dart';

class CategoriesScreen extends StatelessWidget {
  const CategoriesScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Categories')),
      body: ListView(
        padding: const EdgeInsets.all(16),
        children: [
          _SectionCard(
            title: 'Electronics',
            subtitle: 'Live modules',
            color: const Color(0xFF1D4ED8),
            children: const [
              _FeatureChip(label: 'Mobile Phones', icon: Icons.phone_android, enabled: true),
              _FeatureChip(label: 'Mobile Accessories', icon: Icons.headphones, enabled: true),
              _FeatureChip(label: 'All Products', icon: Icons.grid_view_rounded, enabled: true),
            ],
          ),
          const SizedBox(height: 14),
          _SectionCard(
            title: 'Fashion',
            subtitle: 'Upcoming',
            color: const Color(0xFF9333EA),
            children: const [
              _FeatureChip(label: 'Upcoming', icon: Icons.upcoming, enabled: false),
            ],
          ),
          const SizedBox(height: 14),
          _SectionCard(
            title: 'Home & Kitchen',
            subtitle: 'Upcoming',
            color: const Color(0xFF059669),
            children: const [
              _FeatureChip(label: 'Upcoming', icon: Icons.upcoming, enabled: false),
            ],
          ),
          const SizedBox(height: 14),
          _SectionCard(
            title: 'Beauty',
            subtitle: 'Upcoming',
            color: const Color(0xFFDB2777),
            children: const [
              _FeatureChip(label: 'Upcoming', icon: Icons.upcoming, enabled: false),
            ],
          ),
          const SizedBox(height: 14),
          _SectionCard(
            title: 'Grocery',
            subtitle: 'Upcoming',
            color: const Color(0xFFF59E0B),
            children: const [
              _FeatureChip(label: 'Upcoming', icon: Icons.upcoming, enabled: false),
            ],
          ),
        ],
      ),
    );
  }
}

class _SectionCard extends StatelessWidget {
  final String title;
  final String subtitle;
  final Color color;
  final List<Widget> children;

  const _SectionCard({
    required this.title,
    required this.subtitle,
    required this.color,
    required this.children,
  });

  @override
  Widget build(BuildContext context) {
    return Container(
      decoration: BoxDecoration(
        gradient: LinearGradient(
          colors: [color.withOpacity(0.95), color.withOpacity(0.75)],
          begin: Alignment.topLeft,
          end: Alignment.bottomRight,
        ),
        borderRadius: BorderRadius.circular(16),
      ),
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(title, style: const TextStyle(color: Colors.white, fontSize: 20, fontWeight: FontWeight.w700)),
            const SizedBox(height: 4),
            Text(subtitle, style: const TextStyle(color: Colors.white70)),
            const SizedBox(height: 12),
            Wrap(spacing: 8, runSpacing: 8, children: children),
          ],
        ),
      ),
    );
  }
}

class _FeatureChip extends StatelessWidget {
  final String label;
  final IconData icon;
  final bool enabled;

  const _FeatureChip({required this.label, required this.icon, required this.enabled});

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
      decoration: BoxDecoration(
        color: enabled ? Colors.white : Colors.white.withOpacity(0.2),
        borderRadius: BorderRadius.circular(999),
      ),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          Icon(icon, size: 16, color: enabled ? Colors.black87 : Colors.white70),
          const SizedBox(width: 6),
          Text(
            label,
            style: TextStyle(
              color: enabled ? Colors.black87 : Colors.white,
              fontWeight: FontWeight.w600,
            ),
          ),
        ],
      ),
    );
  }
}
