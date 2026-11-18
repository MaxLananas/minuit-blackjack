from decimal import Decimal


def amount_text(valeur, signed=False):
    valeur = Decimal(valeur)
    sign = ""
    if valeur < 0:
        sign = "−"
    elif signed and valeur > 0:
        sign = "+"
    magnitude = abs(valeur)
    integral = int(magnitude)
    text = f"{integral:,}".replace(",", " ")
    fraction = magnitude - integral
    if fraction:
        text += "," + format(fraction, "f").split(".")[1].rstrip("0")
    return sign + text


def round_message(bilan):
    if bilan.annulee:
        return "MANCHE ANNULÉE", "Plus de cartes dans le paquet. Ta mise est rendue."
    if bilan.net > 0:
        return "BIEN JOUÉ", f"Tu repars avec {amount_text(bilan.net, signed=True)} jetons."
    if bilan.net < 0:
        return (
            "PAS CETTE FOIS",
            f"Bilan : {amount_text(bilan.net, signed=True)} jetons.",
        )
    if all(resultat.etiquette == "Égalité" for resultat in bilan.mains):
        return "ÉGALITÉ", "Tu récupères ta mise."
    return "ON FAIT LES COMPTES", "Tes gains et tes pertes s'équilibrent."
