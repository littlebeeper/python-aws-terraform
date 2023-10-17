resource "mongodbatlas_database_user" "admin_user" {
  username           = "admin_user"
  password           = random_password.admin_user_password.result
  project_id         = mongodbatlas_project.this.id
  auth_database_name = "admin"

  roles {
    role_name     = "readWrite"
    database_name = "main_db"
  }

  roles {
    role_name     = "readAnyDatabase"
    database_name = "admin"
  }
}
