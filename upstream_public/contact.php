<?php include 'templates/header.php'; ?>
<h2>Contact (Demo)</h2>
<form method="post" action="/contact.php">
  <label>Name: <input name="name" value="Tester"></label><br>
  <label>Email: <input name="email" value="tester@example.com"></label><br>
  <label>Message:<br><textarea name="message">Hello, this is a demo.</textarea></label><br>
  <button type="submit">Send (demo)</button>
</form>
<?php
if ($_SERVER['REQUEST_METHOD'] === 'POST') {
  $log = ['name'=>$_POST['name'] ?? '','email'=>$_POST['email'] ?? '','message'=>$_POST['message'] ?? '','date'=>date('c')];
  $arr = json_decode(file_get_contents(__DIR__ . '/data/contact_log.json'), true) ?? [];
  $arr[] = $log;
  file_put_contents(__DIR__ . '/data/contact_log.json', json_encode($arr, JSON_PRETTY_PRINT));
  echo '<p class="note">Contact message recorded (demo)</p>';
}
?>
<?php include 'templates/footer.php'; ?>