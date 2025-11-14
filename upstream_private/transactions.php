<?php 
include 'templates/header.php'; 
include_once 'lib.php';
?>
<h2>Transactions (Demo)</h2>
<div style="display:flex;justify-content:space-between;align-items:center;gap:12px;margin-bottom:12px">
  <div style="color:#5b6b7a">List of demo transactions</div>
  <div><button class="btn btn-ghost1" onclick="location.href='/api.php?action=txs'">Open JSON</button> <button class="btn btn-primary" onclick="location.href='/index.php'">Back Home</button></div>
</div>
<?php
$json_response = callDataService('GET', 'txs');
$txs = json_decode($json_response, true);

if (!$txs || !is_array($txs) || (isset($txs['ok']) && $txs['ok'] === false)) {
  echo "<p>Could not load transactions from service.</p>";
  if(isset($txs['error'])) {
    echo "<p style='color:red'>" . htmlspecialchars($txs['error'] . ': ' . ($txs['details'] ?? '')) . "</p>";
  }
  $txs = [];
}

if (count($txs) === 0) {
  echo "<p>No transactions yet. Submit the demo transfer form to create some.</p>";
} else {
  echo "<table class='table'><thead><tr><th>ID</th><th>From</th><th>To</th><th>Amount</th><th>Date</th></tr></thead><tbody>";
  foreach($txs as $t){
    if (is_array($t)) {
       echo "<tr><td>".htmlspecialchars($t['id'] ?? 'N/A')."</td><td>".htmlspecialchars($t['from'] ?? 'N/A')."</td><td>".htmlspecialchars($t['to'] ?? 'N/A')."</td><td>".htmlspecialchars($t['amount'] ?? 'N/A')."</td><td>".htmlspecialchars($t['date'] ?? 'N/A')."</td></tr>";
    }
  }
  echo "</tbody></table>";
}
?>
<?php include 'templates/footer.php'; ?>