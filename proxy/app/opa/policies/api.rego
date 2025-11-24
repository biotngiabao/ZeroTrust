    package authz

    max_auth_age_seconds = 10

    default decision = {
        "allow": false,
        "action": "deny_unauthorized"
    }

    decision = {
        "allow": false,
        "action": "deny_forbidden"
    } if {
        input.score >= 100,
        not public_paths[input.path[0]]
    }

    public_paths = {
        "",             
        "index.php",
        "about.php",
        "contact.php",
        "public",       
        "favicon.ico",
        "docs",
        "openapi.json",
        "token",
        "logout"
    }

    private_user_paths = {
        "dashboard.php",
        "accounts.php",
        "transactions.php",
        "api.php",
        "data.php"
    }

    admin_paths = {
        "admin.php"
    }


    decision = {
        "allow": true,
        "action": "allow"
    } if {
        public_paths[input.path[0]]
    }

    decision = {
        "allow": true,
        "action": "allow"
    } if {
        input.path == ["auth", "callback"]
    }


    decision = {
        "allow": true,
        "action": "allow"
    } if {
        input.path == ["transfer.php"]
        
        input.authenticated == true

        now_seconds := time.now_ns() / 1000000000
        auth_age := now_seconds - input.auth_time
        auth_age <= max_auth_age_seconds
        input.score < 100
    }


    decision = {
        "allow": false,
        "action": "deny_step_up"
    } if {
        input.path == ["transfer.php"]
        now_seconds := time.now_ns() / 1000000000
        auth_age := now_seconds - input.auth_time
        auth_age > max_auth_age_seconds
        input.score < 100
    }

    decision = {
        "allow": true,
        "action": "allow"
    } if {
        admin_paths[input.path[0]]
        input.authenticated == true
        "admin" in input.roles
        input.score < 100
    }

    decision = {
        "allow": false,
        "action": "deny_forbidden"
    } if {
        admin_paths[input.path[0]]
        input.authenticated == true
        not "admin" in input.roles 
        input.score < 100
    }

    decision = {
        "allow": true,
        "action": "allow"
    } if {
        private_user_paths[input.path[0]]
        input.authenticated == true
        input.score < 100
    }

    decision = {
        "allow": true,
        "action": "allow"
    } if {
        input.path[0] == "data.php"
        input.authenticated == true
        input.score < 100
    }


