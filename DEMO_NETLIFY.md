# Configuration Netlify pour la Démo FlorIA

Une fois que tu as l'URL ngrok (ex: `https://abc123.ngrok-free.app`), suis ces étapes pour configurer Netlify.

## Étape 1 : Accéder au Dashboard Netlify

1. Va sur [https://app.netlify.com](https://app.netlify.com)
2. Connecte-toi avec le compte qui héberge le site FlorIA
3. Clique sur le site FlorIA dans la liste

## Étape 2 : Ajouter la Variable d'Environnement

1. Dans le menu du site, clique sur **"Site configuration"** (ou "Site settings")
2. Dans le menu de gauche, clique sur **"Environment variables"**
3. Clique sur **"Add a variable"**
4. Remplis les champs :
   - **Key** : `VITE_API_URL`
   - **Value** : `https://abc123.ngrok-free.app` (ton URL ngrok)
5. Clique sur **"Create variable"**

## Étape 3 : Redéployer le Site

1. Va dans l'onglet **"Deploys"**
2. Clique sur **"Trigger deploy"** → **"Deploy site"**
3. Attends que le déploiement soit terminé (environ 1-2 minutes)

## Étape 4 : Tester

1. Ouvre le site FlorIA sur Netlify
2. Pose une question sur une plante
3. Si tout fonctionne, tu devrais recevoir une réponse du backend !

---

## Dépannage

### Le chat ne répond pas ?

1. Vérifie que ngrok tourne toujours sur le Mac (le terminal doit afficher des logs)
2. Vérifie que l'URL dans Netlify correspond exactement à celle de ngrok
3. Vérifie que le backend est accessible : ouvre `https://ton-url-ngrok.ngrok-free.app/tools` dans un navigateur

### Erreur CORS ?

Le backend est déjà configuré pour accepter toutes les origines. Si tu as une erreur CORS, c'est probablement que le backend n'est pas accessible.

### L'URL ngrok a changé ?

Si tu as redémarré ngrok, l'URL change. Tu dois :
1. Copier la nouvelle URL
2. Mettre à jour la variable `VITE_API_URL` dans Netlify
3. Redéployer le site

---

## Raccourci : Mise à jour rapide de l'URL

Si tu dois changer l'URL rapidement :

1. Dashboard Netlify → Site configuration → Environment variables
2. Clique sur les "..." à côté de `VITE_API_URL` → Edit
3. Change la valeur → Save
4. Deploys → Trigger deploy → Deploy site
