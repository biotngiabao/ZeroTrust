<?php include 'templates/header.php'; ?>
<h2>Admin Panel (Demo)</h2>
<p>No authentication required — this is intentionally open for UI testing.</p>
<p>Config:</p>
<?php
$cfg_file = __DIR__ . '/data/config.json';
$cfg = json_decode(file_get_contents($cfg_file), true) ?? ['vulnerable'=>true];
echo '<pre>'.htmlspecialchars(json_encode($cfg, JSON_PRETTY_PRINT)).'</pre>';
?>
<p>Actions:</p>
<ul>
  <li><a href="/api.php?action=txs">API: Get transactions (JSON)</a></li>
  <li><a href="/api.php?action=transfer_demo">API: Demo transfer (POST)</a></li>
</ul>
<?php include 'templates/footer.php'; ?>