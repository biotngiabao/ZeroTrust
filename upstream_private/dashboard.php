<?php include 'templates/header.php'; ?>
<h2>Dashboard (Demo)</h2>
<p style="color:#5b6b7a">Quick account overview (static demo):</p>
<div class="card" style="display:flex;justify-content:space-between;align-items:center;gap:18px;flex-wrap:wrap">
  <div>
    <h3 style="margin:0">Alice Demo</h3>
    <p style="margin:6px 0">Username: <strong>alice</strong></p>
    <!-- <p style="margin:6px 0">Balance: <strong>12,000</strong></p> -->
  </div>
  <div style="display:flex;gap:8px">
    <button class="btn btn-primary" onclick="location.href='/transfer.php'">Transfer</button>
    <button class="btn btn-ghost1" onclick="location.href='/transactions.php'">Transactions</button>
  </div>
</div>

<div class="card" style="display:flex;justify-content:space-between;align-items:center;gap:18px;flex-wrap:wrap">
  <div>
    <h3 style="margin:0">Bob Demo</h3>
    <p style="margin:6px 0">Username: <strong>bob</strong></p>
    <!-- <p style="margin:6px 0">Balance: <strong>5,400</strong></p> -->
  </div>
  <div style="display:flex;gap:8px">
    <button class="btn btn-ghost1" onclick="location.href='/transactions.php'">Transactions</button>
  </div>
</div>

<?php include 'templates/footer.php'; ?>