# PowerShell script to create the test database
# This can be run after starting the docker-compose services

docker-compose exec -T db psql -U postgres -c "SELECT 1 FROM pg_database WHERE datname='postgres_test'" | Select-String -Pattern "1" -Quiet
if (-not $?) {
    docker-compose exec -T db psql -U postgres -c "CREATE DATABASE postgres_test"
}

