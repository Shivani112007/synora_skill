
# Manage the Synora Flask application service
service { 'synora':
  ensure => running,
  enable => true,
}

# Ensure Nginx is running and enabled
service { 'nginx':
  ensure => running,
  enable => true,
}
