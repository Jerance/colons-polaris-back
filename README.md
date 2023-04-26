# **Colons de Polaris Backend**

## **Installation :**
1. Cloner le dépôt.
2. Installer les dépendances avec <br>
    ```pip install -r requirements.txt```
3. Configurer les variables d'environnement dans un fichier .env.
## **Architecture du Projet :**
L'application est construite selon l'architecture suivante :

### **Modèles de données**
*`/models`*<br>
Les modèles de données sont définis dans le dossier **models**. Nous utilisons Pydantic pour la définition des modèles, qui permet de valider les données d'entrée et de sortie de l'API.

### **Gestion des données**
*`/database`*<br>
Nous utilisons SQLAlchemy pour la gestion de la base de données. Les modèles de données définis dans **models** sont utilisés pour créer les tables de la base de données.<br>
Le dossier **database** contient les fichiers liés à la base de données :

* **`.env`** : ce fichier est utilisé pour stocker les informations sensibles et confidentielles de la configuration de la base de données telles que :
    * **le nom d'utilisateur**
    * **le mot de passe**
    * **l'hôte**
    * **le port**
    * **le nom de la base de données**
* **`config.py`** : ce fichier permet de charger tous les variables d'environnements qui sont stockés dans le fichier de configuration `.env`. Ces informations sont chargées dans notre application via python-dotenv.
* **`db.py`** : ce fichier définit l'objet de la base de données utilisé pour l'accès à la base de données.

### **Routes de l'API**
*`/routes`*<br>
Les routes de l'API sont définies dans le dossier routes. Nous utilisons FastAPI pour la définition des routes et la gestion des requêtes HTTP.

### **Utils**
*`/utils`*<br>
Le dossier utils contient des fichiers qui fournissent des fonctions utiles pour l'application.

### **Tests**
*`/tests`*<br>
Nous utilisons Pytest pour les tests unitaires et d'intégration. Les tests sont stockés dans le dossier tests. Pour exécuter les tests, exécutez pytest dans le terminal.
* **`/tests/postman/`** : ce dossier qui contient des collection Postman pour tester les requêtes API. Cette collection peut être importée dans Postman pour faciliter les tests manuels.

## **Fichiers à la racine du projet:**

* *`.gitignore`* : fichier utilisé par Git pour ignorer certains fichiers ou dossiers lors des commits et des pushs.

* *`authors.md`* : fichier contenant la liste des auteurs et contributeurs du projet.

* *`history.md`* : fichier contenant l'historique des changements et des versions du projet. Il est souvent utilisé en combinaison avec les tags Git pour suivre les différentes versions du projet.

* *`LICENSE.md`* : fichier contenant les informations sur la licence sous laquelle le projet est distribué.

* *`main.py`* : fichier principal de l'application, qui définit l'objet FastAPI, la configuration de base, l'import de tous les routes / schémas ... Ce fichier est le point d'entrée de l'application.

* *`README.md`* : fichier contenant tous les informations sur le projet, telles que son utilisation, son installation, son architecture ...

* *`requirements.txt`* : fichier contenant la liste des dépendances Python nécessaires pour faire fonctionner le projet. Ces dépendances peuvent être installées en utilisant la commande pip install -r requirements.txt.

## **Utilisation :**
Lancer l'application avec la commande uvicorn :
````
uvicorn main:app --reload
````
L'application sera lancée à l'adresse http://localhost:8000.<br>
Pour voir la documentation de l'application avec l'url : http://localhost:8000/docs
