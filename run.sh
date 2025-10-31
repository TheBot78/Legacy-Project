#!/bin/bash

case "$1" in
  front)
    echo "Lancement du FRONT uniquement..."
    docker compose up gwsetup geneweb start rpc --build --remove-orphans
    ;;
  back)
    echo "Lancement du BACK uniquement..."
    docker compose up backend --build --remove-orphans
    ;;
  all|"")
    echo "Lancement de TOUT (front + back)..."
    docker compose up --build --remove-orphans
    ;;
  down)
    echo "Arrêt et suppression des conteneurs..."
    docker compose down --remove-orphans
    ;;
  *)
    echo "Usage: ./run.sh [front|back|all|down]"
    ;;
esac
