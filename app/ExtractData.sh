curl --compressed -X GET "https://diffuseur.datatourisme.fr/webservice/7f2fa3ea017a3b4609a2be86f545bb25/523dc2bd-0eaf-4d95-bded-0c7b96b90e31" --output data.zip

mkdir Data

mkdir Data/JSON

unzip data.zip -d Data/JSON/

rm data.zip