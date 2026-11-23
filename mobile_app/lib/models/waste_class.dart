import 'package:flutter/material.dart';

/// Tempat sampah berdasarkan standar warna pemilahan di Indonesia.
enum WasteBin {
  organik('Organik', 'Tempat sampah hijau', 'Sisa makanan, daun',
      Color(0xFF2E7D32)),
  anorganik('Anorganik', 'Tempat sampah kuning', 'Kaca, logam, plastik',
      Color(0xFFF9A825)),
  kertas('Kertas', 'Tempat sampah biru', 'Kertas, kardus',
      Color(0xFF1565C0));

  const WasteBin(this.label, this.description, this.examples, this.color);

  final String label;
  final String description;
  final String examples;
  final Color color;
}

/// Enam kelas yang dikenali model YOLOv8. Urutannya harus sama dengan
/// indeks kelas saat training (lihat CLASS_NAMES di live_detection.py).
enum WasteClass {
  biodegradable(
    label: 'Organik',
    modelName: 'BIODEGRADABLE',
    icon: Icons.eco_rounded,
    color: Color(0xFF43A047),
    bin: WasteBin.organik,
    decomposeTime: '2 minggu – 6 bulan',
    description:
        'Sisa makanan, daun, kulit buah, dan bahan alami lain yang dapat '
        'terurai oleh mikroorganisme.',
    tips: [
      'Pisahkan dari plastik pembungkus sebelum dibuang.',
      'Olah menjadi kompos atau eco-enzyme di rumah.',
      'Tiriskan sisa makanan berkuah agar tidak berbau.',
    ],
  ),
  cardboard(
    label: 'Kardus',
    modelName: 'CARDBOARD',
    icon: Icons.inventory_2_rounded,
    color: Color(0xFF8D6E63),
    bin: WasteBin.kertas,
    decomposeTime: '± 2 bulan',
    description:
        'Kotak kemasan, karton bergelombang, dan dus bekas paket.',
    tips: [
      'Lipat atau pipihkan agar hemat tempat.',
      'Lepaskan selotip dan label plastik.',
      'Jaga tetap kering; kardus basah sulit didaur ulang.',
    ],
  ),
  glass(
    label: 'Kaca',
    modelName: 'GLASS',
    icon: Icons.wine_bar_rounded,
    color: Color(0xFF26A69A),
    bin: WasteBin.anorganik,
    decomposeTime: '± 1 juta tahun',
    description:
        'Botol, toples, dan wadah kaca lain. Dapat didaur ulang berkali-kali '
        'tanpa menurunkan kualitas.',
    tips: [
      'Bilas sisa isi sebelum dibuang.',
      'Bungkus pecahan kaca dengan kertas tebal dan beri tanda.',
      'Pisahkan tutup logam atau plastiknya.',
    ],
  ),
  metal(
    label: 'Logam',
    modelName: 'METAL',
    icon: Icons.hardware_rounded,
    color: Color(0xFF78909C),
    bin: WasteBin.anorganik,
    decomposeTime: '50 – 500 tahun',
    description:
        'Kaleng minuman, kaleng makanan, tutup botol, dan perkakas logam.',
    tips: [
      'Bilas kaleng lalu pipihkan.',
      'Kaleng aluminium bernilai jual tinggi di bank sampah.',
      'Jangan campur dengan kaleng aerosol bertekanan.',
    ],
  ),
  paper(
    label: 'Kertas',
    modelName: 'PAPER',
    icon: Icons.description_rounded,
    color: Color(0xFF42A5F5),
    bin: WasteBin.kertas,
    decomposeTime: '2 – 6 minggu',
    description: 'Koran, majalah, kertas HVS, buku, dan amplop.',
    tips: [
      'Kumpulkan dalam keadaan kering dan bersih.',
      'Kertas berminyak (bungkus gorengan) masuk residu.',
      'Gunakan kedua sisi kertas sebelum dibuang.',
    ],
  ),
  plastic(
    label: 'Plastik',
    modelName: 'PLASTIC',
    icon: Icons.local_drink_rounded,
    color: Color(0xFFEF6C00),
    bin: WasteBin.anorganik,
    decomposeTime: '20 – 500 tahun',
    description:
        'Botol PET, kantong kresek, gelas plastik, dan kemasan sachet.',
    tips: [
      'Kosongkan, bilas, dan remas botol plastik.',
      'Lepaskan label dan tutup botol (jenis plastiknya berbeda).',
      'Kurangi pemakaian: bawa tas dan botol minum sendiri.',
    ],
  );

  const WasteClass({
    required this.label,
    required this.modelName,
    required this.icon,
    required this.color,
    required this.bin,
    required this.decomposeTime,
    required this.description,
    required this.tips,
  });

  final String label;
  final String modelName;
  final IconData icon;
  final Color color;
  final WasteBin bin;
  final String decomposeTime;
  final String description;
  final List<String> tips;

  static WasteClass fromIndex(int index) => WasteClass.values[index];
}
