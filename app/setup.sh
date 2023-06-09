# Commande pour autoriser l execution du fichier ./setup.sh
# chmod +x myscript.sh

# Construction de l image de l'API
docker image build -t api_image -f ./Dockerfile/api_image.Dockerfile .

# Construction de l image de streamlit
docker image build -t streamlit_image -f ./Dockerfile/Dockerfile_streamlit .

# Création du réseau externe
docker network create -d bridge dock_net

# Lancement des conteneurs
docker-compose up