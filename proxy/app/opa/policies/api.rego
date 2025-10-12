package authz

default allow = false

allow if {
    input.path[0] == "public"
}
allow if {
    input.path[0] == "docs"
}

allow if {
    some "index.php" in input.path
}

allow if {
  some "dashboard.php" in input.path
  some "finance" in input.roles
}

allow if {
  some "accounts.php" in input.path
  
}

allow if {
  some "finance.php" in input.path
}

