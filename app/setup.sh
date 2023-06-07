# Construction de l'image de l'API
docker image build -t api -f ./Dockerfile/api.Dockerfile .

# Création du réseau externe
docker network create -d bridge api_net

# Lancement des conteneurs
docker-compose up