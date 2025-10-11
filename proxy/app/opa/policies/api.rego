package authz

default allow = false


allow if {
  input.path == ["index.php"]
}

allow if {
  input.path == ["about.php"]
}

allow if {
  input.path == ["account.php"]
}

allow if {
  input.path == ["finance.php"]
}

