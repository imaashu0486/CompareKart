import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../providers/auth_provider.dart';
import '../providers/watchlist_provider.dart';

class ProfileScreen extends StatelessWidget {
  const ProfileScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Consumer2<AuthProvider, WatchlistProvider>(
      builder: (context, auth, watchlist, _) {
        final displayName = (auth.fullName?.trim().isNotEmpty ?? false) ? auth.fullName! : auth.userId ?? 'User';

        return Scaffold(
          appBar: AppBar(title: const Text('Profile')),
          body: ListView(
            padding: const EdgeInsets.all(16),
            children: [
              Container(
                padding: const EdgeInsets.all(16),
                decoration: BoxDecoration(
                  gradient: const LinearGradient(
                    colors: [Color(0xFF0EA5E9), Color(0xFF2563EB)],
                    begin: Alignment.topLeft,
                    end: Alignment.bottomRight,
                  ),
                  borderRadius: BorderRadius.circular(16),
                ),
                child: Row(
                  children: [
                    const CircleAvatar(
                      radius: 28,
                      backgroundColor: Colors.white,
                      child: Icon(Icons.person, size: 28, color: Color(0xFF2563EB)),
                    ),
                    const SizedBox(width: 12),
                    Expanded(
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text(displayName, style: const TextStyle(color: Colors.white, fontSize: 18, fontWeight: FontWeight.w700)),
                          const SizedBox(height: 4),
                          Text(auth.email ?? 'No email added', style: const TextStyle(color: Colors.white70)),
                        ],
                      ),
                    )
                  ],
                ),
              ),
              const SizedBox(height: 16),
              _ProfileTile(
                icon: Icons.bookmark_added_outlined,
                title: 'Watchlist Items',
                subtitle: '${watchlist.count} saved offers',
              ),
              const _ProfileTile(
                icon: Icons.notifications_active_outlined,
                title: 'Price Drop Alerts',
                subtitle: 'Upcoming',
              ),
              const _ProfileTile(
                icon: Icons.security_outlined,
                title: 'Secure Login',
                subtitle: 'Enabled with user ID + password',
              ),
              const _ProfileTile(
                icon: Icons.workspace_premium_outlined,
                title: 'CompareKart Pro',
                subtitle: 'Upcoming',
              ),
              const SizedBox(height: 12),
              OutlinedButton.icon(
                onPressed: () => auth.logout(),
                icon: const Icon(Icons.logout),
                label: const Text('Sign out'),
              ),
            ],
          ),
        );
      },
    );
  }
}

class _ProfileTile extends StatelessWidget {
  final IconData icon;
  final String title;
  final String subtitle;

  const _ProfileTile({required this.icon, required this.title, required this.subtitle});

  @override
  Widget build(BuildContext context) {
    return Card(
      child: ListTile(
        leading: Icon(icon),
        title: Text(title),
        subtitle: Text(subtitle),
      ),
    );
  }
}
