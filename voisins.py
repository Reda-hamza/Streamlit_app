import streamlit as st
import pandas as pd
from datetime import datetime
import json
import os

# Configuration de la page
st.set_page_config(
    page_title="Gestion Cotisations Voisins",
    page_icon="🏢",
    layout="wide"
)

# Fichiers de sauvegarde
FICHIER_VOISINS = "voisins.json"
FICHIER_COTISATIONS = "cotisations.json"
FICHIER_PAIEMENTS = "paiements.json"

# Fonction pour charger les données
def charger_donnees(fichier, defaut=[]):
    if os.path.exists(fichier):
        with open(fichier, 'r', encoding='utf-8') as f:
            return json.load(f)
    return defaut

# Fonction pour sauvegarder les données
def sauvegarder_donnees(fichier, donnees):
    with open(fichier, 'w', encoding='utf-8') as f:
        json.dump(donnees, f, ensure_ascii=False, indent=2)

# Initialisation des données
if 'voisins' not in st.session_state:
    st.session_state.voisins = charger_donnees(FICHIER_VOISINS, [])
if 'cotisations' not in st.session_state:
    st.session_state.cotisations = charger_donnees(FICHIER_COTISATIONS, [])
if 'paiements' not in st.session_state:
    st.session_state.paiements = charger_donnees(FICHIER_PAIEMENTS, [])

# Titre principal
st.title("🏢 Gestion des Cotisations de Voisinage")

# Menu de navigation
menu = st.sidebar.selectbox(
    "Menu",
    ["🏠 Gestion des Voisins", "💰 Cotisations", "💳 Paiements", "📈 Rapports"]
)

# ===== GESTION DES VOISINS =====
if menu == "🏠 Gestion des Voisins":
    st.header("Gestion des Voisins")
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.subheader("Ajouter un voisin")
        
        with st.form("form_voisin"):
            etage = st.number_input("Étage", min_value=0, max_value=20, value=0, step=1)
            numero_appt = st.text_input("Numéro d'appartement", value="")
            nom_personne = st.text_input("Nom (facultatif)", value="")
            
            submitted = st.form_submit_button("Ajouter")
            
            if submitted:
                if numero_appt:
                    # Vérifier si l'appartement existe déjà
                    existe = any(v['etage'] == etage and v['numero_appt'] == numero_appt 
                               for v in st.session_state.voisins)
                    
                    if not existe:
                        nouveau_voisin = {
                            'id': len(st.session_state.voisins) + 1,
                            'etage': etage,
                            'numero_appt': numero_appt,
                            'nom': nom_personne if nom_personne else f"Appartement {numero_appt}",
                            'date_ajout': datetime.now().strftime("%Y-%m-%d")
                        }
                        st.session_state.voisins.append(nouveau_voisin)
                        sauvegarder_donnees(FICHIER_VOISINS, st.session_state.voisins)
                        st.success(f"Voisin ajouté : Étage {etage}, Appt {numero_appt}")
                        st.rerun()
                    else:
                        st.error("Cet appartement existe déjà!")
                else:
                    st.error("Le numéro d'appartement est obligatoire!")
    
    with col2:
        st.subheader("Liste des Voisins")
        
        if st.session_state.voisins:
            df_voisins = pd.DataFrame(st.session_state.voisins)
            df_voisins = df_voisins.sort_values(['etage', 'numero_appt'])
            
            # Affichage avec possibilité de suppression
            for idx, voisin in df_voisins.iterrows():
                col_a, col_b = st.columns([4, 1])
                with col_a:
                    st.write(f"**Étage {voisin['etage']} - Appt {voisin['numero_appt']}** : {voisin['nom']}")
                with col_b:
                    if st.button("🗑️", key=f"del_{voisin['id']}"):
                        st.session_state.voisins = [v for v in st.session_state.voisins if v['id'] != voisin['id']]
                        sauvegarder_donnees(FICHIER_VOISINS, st.session_state.voisins)
                        st.rerun()
        else:
            st.info("Aucun voisin enregistré")

# ===== COTISATIONS =====
elif menu == "💰 Cotisations":
    st.header("Gestion des Cotisations")
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.subheader("Nouvelle Cotisation")
        
        with st.form("form_cotisation"):
            titre = st.text_input("Titre de la cotisation")
            montant = st.number_input("Montant par appartement (DH)", min_value=0.0, step=10.0)
            type_cotisation = st.selectbox("Type", ["Achat", "Service"])
            description = st.text_area("Description")
            date_cotisation = st.date_input("Date")
            
            submitted = st.form_submit_button("Créer la cotisation")
            
            if submitted:
                if titre and montant > 0:
                    nouvelle_cotisation = {
                        'id': len(st.session_state.cotisations) + 1,
                        'titre': titre,
                        'montant': montant,
                        'type': type_cotisation,
                        'description': description,
                        'date': str(date_cotisation),
                        'date_creation': datetime.now().strftime("%Y-%m-%d %H:%M")
                    }
                    st.session_state.cotisations.append(nouvelle_cotisation)
                    sauvegarder_donnees(FICHIER_COTISATIONS, st.session_state.cotisations)
                    st.success(f"Cotisation '{titre}' créée!")
                    st.rerun()
                else:
                    st.error("Veuillez remplir tous les champs obligatoires!")
    
    with col2:
        st.subheader("Liste des Cotisations")
        
        if st.session_state.cotisations:
            for cotisation in reversed(st.session_state.cotisations):
                with st.expander(f"{cotisation['titre']} - {cotisation['montant']} DH ({cotisation['type']})"):
                    st.write(f"**Description:** {cotisation['description']}")
                    st.write(f"**Date:** {cotisation['date']}")
                    st.write(f"**Type:** {cotisation['type']}")
                    
                    if st.button("🗑️ Supprimer", key=f"del_cot_{cotisation['id']}"):
                        st.session_state.cotisations = [c for c in st.session_state.cotisations 
                                                        if c['id'] != cotisation['id']]
                        sauvegarder_donnees(FICHIER_COTISATIONS, st.session_state.cotisations)
                        st.rerun()
        else:
            st.info("Aucune cotisation enregistrée")

# ===== PAIEMENTS =====
elif menu == "💳 Paiements":
    st.header("Enregistrement des Paiements")
    
    if not st.session_state.voisins:
        st.warning("Veuillez d'abord ajouter des voisins dans le menu 'Gestion des Voisins'")
    elif not st.session_state.cotisations:
        st.warning("Veuillez d'abord créer une cotisation dans le menu 'Cotisations'")
    else:
        col1, col2 = st.columns([1, 2])
        
        with col1:
            st.subheader("Nouveau Paiement")
            
            with st.form("form_paiement"):
                # Sélection du voisin
                voisins_options = {
                    f"Étage {v['etage']} - Appt {v['numero_appt']} ({v['nom']})": v['id'] 
                    for v in st.session_state.voisins
                }
                voisin_selectionne = st.selectbox("Voisin", list(voisins_options.keys()))
                
                # Sélection de la cotisation
                cotisations_options = {
                    f"{c['titre']} - {c['montant']} DH": c['id'] 
                    for c in st.session_state.cotisations
                }
                cotisation_selectionnee = st.selectbox("Cotisation", list(cotisations_options.keys()))
                
                montant_paye = st.number_input("Montant payé (DH)", min_value=0.0, step=10.0)
                date_paiement = st.date_input("Date de paiement")
                mode_paiement = st.selectbox("Mode de paiement", ["Espèces", "Virement", "Chèque"])
                note = st.text_input("Note (facultatif)", placeholder="Ex: Premier versement, Paiement complet...")
                
                submitted = st.form_submit_button("Enregistrer le paiement")
                
                if submitted:
                    if montant_paye > 0:
                        voisin_id = voisins_options[voisin_selectionne]
                        cotisation_id = cotisations_options[cotisation_selectionnee]
                        
                        # Récupérer le montant de la cotisation
                        cotisation = next(c for c in st.session_state.cotisations if c['id'] == cotisation_id)
                        
                        nouveau_paiement = {
                            'id': len(st.session_state.paiements) + 1 if st.session_state.paiements else 1,
                            'voisin_id': voisin_id,
                            'cotisation_id': cotisation_id,
                            'montant_paye': montant_paye,
                            'montant_du': cotisation['montant'],
                            'date_paiement': str(date_paiement),
                            'mode_paiement': mode_paiement,
                            'note': note,
                            'date_enregistrement': datetime.now().strftime("%Y-%m-%d %H:%M")
                        }
                        st.session_state.paiements.append(nouveau_paiement)
                        sauvegarder_donnees(FICHIER_PAIEMENTS, st.session_state.paiements)
                        
                        if montant_paye >= cotisation['montant']:
                            st.success(f"✅ Paiement complet enregistré!")
                        elif montant_paye < cotisation['montant']:
                            st.success(f"⚠️ Paiement partiel enregistré ({montant_paye}/{cotisation['montant']} DH)")
                        else:
                            st.info(f"💰 Paiement excédentaire enregistré (+{montant_paye - cotisation['montant']} DH)")
                        st.rerun()
                    else:
                        st.error("Le montant doit être supérieur à 0!")
        
        with col2:
            st.subheader("Liste des Paiements")
            
            # Filtre par voisin
            filtre_options = ["Tous"] + [f"Étage {v['etage']} - Appt {v['numero_appt']}" 
                                         for v in st.session_state.voisins]
            filtre_voisin = st.selectbox("Filtrer par voisin", filtre_options)
            
            if st.session_state.paiements:
                paiements_affiches = st.session_state.paiements.copy()
                
                # Appliquer le filtre
                if filtre_voisin != "Tous":
                    voisin_filtre = next(v for v in st.session_state.voisins 
                                        if f"Étage {v['etage']} - Appt {v['numero_appt']}" == filtre_voisin)
                    paiements_affiches = [p for p in paiements_affiches 
                                         if p['voisin_id'] == voisin_filtre['id']]
                
                for paiement in reversed(paiements_affiches):
                    voisin = next(v for v in st.session_state.voisins if v['id'] == paiement['voisin_id'])
                    cotisation = next(c for c in st.session_state.cotisations if c['id'] == paiement['cotisation_id'])
                    
                    # Déterminer le statut
                    if paiement['montant_paye'] >= paiement['montant_du']:
                        if paiement['montant_paye'] > paiement['montant_du']:
                            statut = "💰 Excédentaire"
                            couleur = "blue"
                        else:
                            statut = "✅ Complet"
                            couleur = "green"
                    else:
                        statut = "⚠️ Partiel"
                        couleur = "orange"
                    
                    with st.expander(f"{statut} - {voisin['nom']} - {cotisation['titre']} ({paiement['date_paiement']})"):
                        col_a, col_b = st.columns(2)
                        with col_a:
                            st.write(f"**Voisin:** {voisin['nom']}")
                            st.write(f"**Étage/Appt:** {voisin['etage']}/{voisin['numero_appt']}")
                            st.write(f"**Cotisation:** {cotisation['titre']}")
                            st.write(f"**Montant payé:** {paiement['montant_paye']} DH")
                            st.write(f"**Montant dû:** {paiement['montant_du']} DH")
                        
                        with col_b:
                            st.write(f"**Date:** {paiement['date_paiement']}")
                            st.write(f"**Mode:** {paiement['mode_paiement']}")
                            if paiement.get('note'):
                                st.write(f"**Note:** {paiement['note']}")
                            
                            if paiement['montant_paye'] > paiement['montant_du']:
                                excedent = paiement['montant_paye'] - paiement['montant_du']
                                st.info(f"Excédent: +{excedent} DH")
                            elif paiement['montant_paye'] < paiement['montant_du']:
                                reste = paiement['montant_du'] - paiement['montant_paye']
                                st.warning(f"Reste à payer: {reste} DH")
                        
                        # Boutons de modification et suppression
                        col_mod, col_sup = st.columns(2)
                        with col_mod:
                            if st.button("✏️ Modifier", key=f"mod_{paiement['id']}"):
                                st.session_state[f'edit_{paiement["id"]}'] = True
                                st.rerun()
                        
                        with col_sup:
                            if st.button("🗑️ Supprimer", key=f"del_{paiement['id']}"):
                                st.session_state.paiements = [p for p in st.session_state.paiements 
                                                             if p['id'] != paiement['id']]
                                sauvegarder_donnees(FICHIER_PAIEMENTS, st.session_state.paiements)
                                st.rerun()
                        
                        # Formulaire de modification
                        if st.session_state.get(f'edit_{paiement["id"]}', False):
                            st.write("---")
                            st.write("**Modifier le paiement:**")
                            
                            with st.form(f"form_edit_{paiement['id']}"):
                                new_montant = st.number_input("Nouveau montant", 
                                                             value=float(paiement['montant_paye']), 
                                                             min_value=0.0, step=10.0)
                                new_date = st.date_input("Nouvelle date", 
                                                        value=datetime.strptime(paiement['date_paiement'], "%Y-%m-%d"))
                                new_mode = st.selectbox("Nouveau mode", 
                                                       ["Espèces", "Virement", "Chèque"],
                                                       index=["Espèces", "Virement", "Chèque"].index(paiement['mode_paiement']))
                                new_note = st.text_input("Nouvelle note", value=paiement.get('note', ''))
                                
                                col1, col2 = st.columns(2)
                                with col1:
                                    submit_edit = st.form_submit_button("💾 Sauvegarder")
                                with col2:
                                    cancel_edit = st.form_submit_button("❌ Annuler")
                                
                                if submit_edit:
                                    for p in st.session_state.paiements:
                                        if p['id'] == paiement['id']:
                                            p['montant_paye'] = new_montant
                                            p['date_paiement'] = str(new_date)
                                            p['mode_paiement'] = new_mode
                                            p['note'] = new_note
                                    sauvegarder_donnees(FICHIER_PAIEMENTS, st.session_state.paiements)
                                    del st.session_state[f'edit_{paiement["id"]}']
                                    st.success("Paiement modifié!")
                                    st.rerun()
                                
                                if cancel_edit:
                                    del st.session_state[f'edit_{paiement["id"]}']
                                    st.rerun()
            else:
                st.info("Aucun paiement enregistré")


# ===== RAPPORTS =====
elif menu == "📈 Rapports":
    st.header("Rapports et Statistiques")
    
    # Onglets pour différents rapports
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📊 Vue d'ensemble", 
        "❌ Impayés Totaux", 
        "⚠️ Paiements Partiels", 
        "💰 Détails par Cotisation",
        "📈 Classement Voisins"
    ])
    
    with tab1:
        st.subheader("Vue d'ensemble")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Nombre de voisins", len(st.session_state.voisins))
        
        with col2:
            total_cotisations = sum(c['montant'] for c in st.session_state.cotisations) * len(st.session_state.voisins)
            st.metric("Total attendu", f"{total_cotisations:.2f} DH")
        
        with col3:
            total_paye = sum(p['montant_paye'] for p in st.session_state.paiements)
            st.metric("Total payé", f"{total_paye:.2f} DH")
        
        with col4:
            reste_total = total_cotisations - total_paye
            st.metric("Reste à collecter", f"{reste_total:.2f} DH")
        
        # Résumé par voisin
        st.subheader("Résumé des paiements par voisin")
        
        if st.session_state.voisins and st.session_state.cotisations:
            data_resume = []
            
            for voisin in st.session_state.voisins:
                # Calculer total dû
                total_du = sum(c['montant'] for c in st.session_state.cotisations)
                
                # Calculer total payé (somme de TOUS les paiements du voisin)
                paiements_voisin = [p for p in st.session_state.paiements if p['voisin_id'] == voisin['id']]
                total_paye_voisin = sum(p['montant_paye'] for p in paiements_voisin)
                
                # Calculer reste
                reste = total_du - total_paye_voisin
                
                # Taux de paiement
                taux = (total_paye_voisin / total_du * 100) if total_du > 0 else 0
                
                data_resume.append({
                    'Étage': voisin['etage'],
                    'Appartement': voisin['numero_appt'],
                    'Nom': voisin['nom'],
                    'Total Dû (DH)': total_du,
                    'Total Payé (DH)': total_paye_voisin,
                    'Reste (DH)': reste,
                    'Taux (%)': taux
                })
            
            df_resume = pd.DataFrame(data_resume)
            df_resume = df_resume.sort_values('Reste (DH)', ascending=False)
            
            # Affichage avec code couleur
            st.dataframe(
                df_resume.style.background_gradient(
                    subset=['Taux (%)'], 
                    cmap='RdYlGn',
                    vmin=0,
                    vmax=100
                ),
                hide_index=True,
                use_container_width=True
            )
    
    with tab2:
        st.subheader("Impayés Totaux par Voisin")
        
        if st.session_state.voisins and st.session_state.cotisations:
            # Calculer les impayés totaux
            impaye_data = []
            total_impaye_general = 0
            
            for voisin in st.session_state.voisins:
                # Total dû pour toutes les cotisations
                total_du = sum(c['montant'] for c in st.session_state.cotisations)
                
                # Total payé (somme de tous les paiements)
                paiements_voisin = [p for p in st.session_state.paiements if p['voisin_id'] == voisin['id']]
                total_paye = sum(p['montant_paye'] for p in paiements_voisin)
                
                # Calcul du reste
                reste = total_du - total_paye
                
                if reste > 0:
                    impaye_data.append({
                        'voisin': voisin,
                        'total_du': total_du,
                        'total_paye': total_paye,
                        'reste': reste
                    })
                    total_impaye_general += reste
            
            # Afficher le total général des impayés
            st.error(f"### 💰 Total des impayés : {total_impaye_general:.2f} DH")
            
            if impaye_data:
                st.write("---")
                # Trier par montant impayé décroissant
                impaye_data.sort(key=lambda x: x['reste'], reverse=True)
                
                for item in impaye_data:
                    voisin = item['voisin']
                    with st.expander(
                        f"❌ {voisin['nom']} - Étage {voisin['etage']}, Appt {voisin['numero_appt']} "
                        f"→ Reste : {item['reste']:.2f} DH"
                    ):
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            st.metric("Total Dû", f"{item['total_du']:.2f} DH")
                        with col2:
                            st.metric("Total Payé", f"{item['total_paye']:.2f} DH")
                        with col3:
                            st.metric("Reste", f"{item['reste']:.2f} DH", delta=f"-{item['reste']:.2f}")
                        
                        # Détail par cotisation
                        st.write("**Détail par cotisation:**")
                        for cotisation in st.session_state.cotisations:
                            # Paiements pour cette cotisation
                            paiements_cot = [p for p in st.session_state.paiements 
                                           if p['voisin_id'] == voisin['id'] 
                                           and p['cotisation_id'] == cotisation['id']]
                            
                            total_paye_cot = sum(p['montant_paye'] for p in paiements_cot)
                            reste_cot = cotisation['montant'] - total_paye_cot
                            
                            if reste_cot > 0:
                                st.write(f"  • {cotisation['titre']}: "
                                        f"{total_paye_cot:.2f}/{cotisation['montant']:.2f} DH "
                                        f"(Reste: {reste_cot:.2f} DH)")
                            elif len(paiements_cot) > 1:
                                st.write(f"  • ✅ {cotisation['titre']}: Payé en {len(paiements_cot)} versements")
                            else:
                                st.write(f"  • ✅ {cotisation['titre']}: Payé")
            else:
                st.success("🎉 Aucun impayé ! Tous les voisins sont à jour.")
        else:
            st.info("Aucune donnée disponible")
    
    with tab3:
        st.subheader("Paiements Partiels par Cotisation")
        
        if st.session_state.cotisations and st.session_state.voisins:
            for cotisation in st.session_state.cotisations:
                st.write(f"### {cotisation['titre']} ({cotisation['montant']} DH)")
                
                paiements_partiels_cot = []
                
                for voisin in st.session_state.voisins:
                    # Tous les paiements de ce voisin pour cette cotisation
                    paiements_voisin_cot = [p for p in st.session_state.paiements 
                                           if p['voisin_id'] == voisin['id'] 
                                           and p['cotisation_id'] == cotisation['id']]
                    
                    total_paye = sum(p['montant_paye'] for p in paiements_voisin_cot)
                    
                    # Si paiement partiel (payé moins que le montant dû)
                    if 0 < total_paye < cotisation['montant']:
                        nb_versements = len(paiements_voisin_cot)
                        reste = cotisation['montant'] - total_paye
                        pourcentage = (total_paye / cotisation['montant']) * 100
                        
                        paiements_partiels_cot.append({
                            'voisin': voisin,
                            'total_paye': total_paye,
                            'reste': reste,
                            'pourcentage': pourcentage,
                            'nb_versements': nb_versements
                        })
                
                if paiements_partiels_cot:
                    for item in paiements_partiels_cot:
                        voisin = item['voisin']
                        st.warning(
                            f"⚠️ **{voisin['nom']}** (Étage {voisin['etage']}, Appt {voisin['numero_appt']}) - "
                            f"{item['nb_versements']} versement(s) - "
                            f"Payé: {item['total_paye']:.2f}/{cotisation['montant']:.2f} DH "
                            f"({item['pourcentage']:.1f}%) - "
                            f"Reste: {item['reste']:.2f} DH"
                        )
                else:
                    st.success("✅ Aucun paiement partiel pour cette cotisation")
                
                st.divider()
        else:
            st.info("Aucune donnée disponible")
    
    with tab4:
        st.subheader("Détails par cotisation")
        
        if st.session_state.cotisations:
            for cotisation in st.session_state.cotisations:
                with st.expander(f"{cotisation['titre']} - {cotisation['montant']} DH par appartement"):
                    st.write(f"**Type:** {cotisation['type']}")
                    st.write(f"**Description:** {cotisation['description']}")
                    st.write(f"**Date:** {cotisation['date']}")
                    
                    # Tableau récapitulatif
                    total_attendu = cotisation['montant'] * len(st.session_state.voisins)
                    
                    # Total reçu pour cette cotisation (somme de tous les paiements)
                    paiements_cotisation = [p for p in st.session_state.paiements 
                                           if p['cotisation_id'] == cotisation['id']]
                    total_recu = sum(p['montant_paye'] for p in paiements_cotisation)
                    
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Total attendu", f"{total_attendu:.2f} DH")
                    with col2:
                        st.metric("Total reçu", f"{total_recu:.2f} DH")
                    with col3:
                        st.metric("Reste à recevoir", f"{total_attendu - total_recu:.2f} DH")
                    
                    # Détails par voisin
                    st.write("**Détails par voisin:**")
                    for voisin in st.session_state.voisins:
                        # Tous les paiements de ce voisin pour cette cotisation
                        paiements_voisin = [p for p in paiements_cotisation 
                                          if p['voisin_id'] == voisin['id']]
                        
                        total_paye_voisin = sum(p['montant_paye'] for p in paiements_voisin)
                        nb_versements = len(paiements_voisin)
                        
                        if total_paye_voisin >= cotisation['montant']:
                            if total_paye_voisin > cotisation['montant']:
                                excedent = total_paye_voisin - cotisation['montant']
                                statut = f"💰 Payé avec excédent (+{excedent:.2f} DH)"
                            else:
                                statut = "✅ Payé complet"
                            
                            if nb_versements > 1:
                                statut += f" en {nb_versements} versements"
                        elif total_paye_voisin > 0:
                            reste = cotisation['montant'] - total_paye_voisin
                            statut = f"⚠️ Partiel: {total_paye_voisin:.2f}/{cotisation['montant']:.2f} DH (Reste: {reste:.2f} DH)"
                            if nb_versements > 1:
                                statut += f" - {nb_versements} versements"
                        else:
                            statut = f"❌ Non payé (Dû: {cotisation['montant']:.2f} DH)"
                        
                        st.write(f"{statut} - Étage {voisin['etage']}, Appt {voisin['numero_appt']} ({voisin['nom']})")
        else:
            st.info("Aucune cotisation enregistrée")
    
    with tab5:
        st.subheader("Classement des Voisins")
        
        if st.session_state.voisins and st.session_state.cotisations:
            # Calculer les données pour le classement
            classement_data = []
            
            for voisin in st.session_state.voisins:
                total_du = sum(c['montant'] for c in st.session_state.cotisations)
                paiements_voisin = [p for p in st.session_state.paiements if p['voisin_id'] == voisin['id']]
                total_paye = sum(p['montant_paye'] for p in paiements_voisin)
                
                classement_data.append({
                    'Nom': voisin['nom'],
                    'Étage': voisin['etage'],
                    'Appt': voisin['numero_appt'],
                    'Total Payé': total_paye,
                    'Total Dû': total_du,
                    'Différence': total_paye - total_du
                })
            
            df_classement = pd.DataFrame(classement_data)
            
            # Graphique des meilleurs payeurs
            st.write("### 🏆 Top 5 des meilleurs payeurs")
            top_payeurs = df_classement.nlargest(5, 'Total Payé')
            
            if not top_payeurs.empty:
                fig_top = pd.DataFrame({
                    'Voisin': top_payeurs['Nom'].astype(str) + ' (E' + top_payeurs['Étage'].astype(str) + '/A' + top_payeurs['Appt'].astype(str) + ')',
                    'Montant Payé (DH)': top_payeurs['Total Payé']
                })
                st.bar_chart(fig_top.set_index('Voisin'))
                
                for idx, row in top_payeurs.iterrows():
                    if row['Différence'] > 0:
                        st.success(f"🌟 {row['Nom']} - Payé: {row['Total Payé']:.2f} DH (Excédent: +{row['Différence']:.2f} DH)")
                    else:
                        st.info(f"✅ {row['Nom']} - Payé: {row['Total Payé']:.2f} DH")
            
            st.write("---")
            
            # Graphique des moins bons payeurs
            st.write("### ⚠️ Top 5 des payeurs à relancer")
            moins_payeurs = df_classement.nsmallest(5, 'Total Payé')
            
            if not moins_payeurs.empty:
                fig_moins = pd.DataFrame({
                    'Voisin': moins_payeurs['Nom'].astype(str) + ' (E' + moins_payeurs['Étage'].astype(str) + '/A' + moins_payeurs['Appt'].astype(str) + ')',
                    'Montant Payé (DH)': moins_payeurs['Total Payé']
                })
                st.bar_chart(fig_moins.set_index('Voisin'))
                
                for idx, row in moins_payeurs.iterrows():
                    reste = row['Total Dû'] - row['Total Payé']
                    pourcentage = (row['Total Payé'] / row['Total Dû'] * 100) if row['Total Dû'] > 0 else 0
                    
                    if reste > 0:
                        st.warning(f"❌ {row['Nom']} - Payé: {row['Total Payé']:.2f}/{row['Total Dû']:.2f} DH ({pourcentage:.1f}%) - Reste: {reste:.2f} DH")
                    else:
                        st.success(f"✅ {row['Nom']} - À jour")
            
            st.write("---")
            
            # Tableau complet
            st.write("### 📊 Tableau de classement complet")
            df_affichage = df_classement.sort_values('Total Payé', ascending=False)
            st.dataframe(
                df_affichage.style.background_gradient(
                    subset=['Total Payé'], 
                    cmap='RdYlGn'
                ),
                hide_index=True,
                use_container_width=True
            )
        else:
            st.info("Aucune donnée disponible pour générer le classement")

# Footer
st.sidebar.markdown("---")
st.sidebar.info("Application de gestion des cotisations de voisinage")