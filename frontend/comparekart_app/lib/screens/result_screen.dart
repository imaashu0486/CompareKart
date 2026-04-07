/// Result Screen
/// Displays search results with filtering and sorting

import 'package:flutter/material.dart';

class ResultScreen extends StatelessWidget {
  const ResultScreen({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Results'),
      ),
      body: const Center(
        child: Text('Results Screen'),
      ),
    );
  }
}
