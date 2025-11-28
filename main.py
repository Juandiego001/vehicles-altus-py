import re
import urllib3
import requests
from utils import send_mail
from datetime import datetime, timedelta
from config import MAIL_RECIPIENTS, r, URL_VEHICLE, URL_FOR_REQUEST, URL_OPENAPI, access_logger, error_logger


urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


month_map = {
    1: "January", 2: "February", 3: "March", 4: "April",
    5: "May", 6: "June", 7: "July", 8: "August",
    9: "September", 10: "October", 11: "November", 12: "December"
}


def get_vehicles_data(alignments: list[dict]):
    '''Get vehicles data for every alignment registered'''

    final_data = []
    for alignment in alignments:
        params = {
            'serialNumber': alignment['serial'],
            'username': 'andresleon'
        }
        try:
            response = requests.get(
                URL_VEHICLE, params=params, verify=False, timeout=35)
            response.raise_for_status()
            data = response.json()
            needed_keys = ["version", "specs", "specsExpiration"]

            data = {each_key: data[each_key] for each_key in needed_keys}
            version: dict = data.get("version")
            specs = data.get("specs")
            specs_expiration = data.get("specsExpiration")

            variables = (version, specs, specs_expiration)
            if any(v is None for v in variables):
                continue

            final_data.append({
                'serial': alignment['serial'],
                'version': ' '.join(x for x in version.values() if isinstance(x, str)),
                'specs': f"{month_map[specs['month']]} {specs['year']} - {specs['name']}",
                'specs_expiration': f"{month_map[specs_expiration['month']]} {specs_expiration['year']}",
                'date': alignment['date'],
                'date_altus': alignment['date_altus'],
                'vehicle': alignment['vehicle'],
                'url': alignment['url'],
                'type': alignment['type']
            })
            break

        except requests.exceptions.HTTPError as http_err:
            error_logger.exception(f"Error HTTP: {http_err}")
            error_logger.exception(
                "El servidor respondió con un error. Deteniendo.")
        except requests.exceptions.ConnectionError as conn_err:
            error_logger.exception(f"Error de Conexión: {conn_err}")
            error_logger.exception(
                f"No se pudo conectar a '{URL_FOR_REQUEST}'. ¿Está el servidor encendido?")
        except requests.exceptions.Timeout:
            error_logger.exception(
                "Error: La petición (timeout) de 10 segundos fue superada.")
        except requests.exceptions.RequestException as err:
            error_logger.exception(
                f"Ocurrió un error inesperado en la petición: {err}")

    return final_data


def get_date(filename: str):
    '''Get date from the filename'''

    patron = r"(\d{2}-\d{2}-\d{4}_\d{2}-\d{2})"
    match = re.search(patron, filename)

    if match:
        return datetime.strptime(match.group(1), "%d-%m-%Y_%H-%M") + timedelta(hours=8)
    else:
        return None


def get_altus_data(date_since: datetime, date_until: datetime):
    '''Get Altus Data'''

    alignments: list[dict] = []
    page_size = 120
    page_number = 1
    keep_fetching = True
    while keep_fetching:
        params = {
            'pageNumber': page_number,
            'pageSize': page_size,
            'needValidSession': False
        }
        try:
            response = requests.get(
                URL_FOR_REQUEST, params=params, verify=False, timeout=35)
            response.raise_for_status()
            data: dict = response.json()
            cards = data.get("cards", [])
            if not cards:
                keep_fetching = False
                break

            needed_keys = ["fileName", "hash",
                           "date", "editedName", "vehicleData"]
            for card in cards:
                card = {each_key: card[each_key] for each_key in needed_keys}
                card_filename: str = card.get("fileName")
                card_date = card.get("date")
                card_hash = card.get("hash")
                card_name: str = card.get("editedName")
                card_vehicle_data = card.get("vehicleData")

                variables = (card_filename, card_date, card_hash,
                             card_name, card_vehicle_data)
                if any(v is None for v in variables):
                    continue

                try:
                    alignment_date: datetime | None = get_date(card_filename)
                    serial = card_filename.split('_')[1]

                    altus_date = datetime.fromisoformat(
                        card_date) - timedelta(hours=5)
                    if altus_date <= date_until and altus_date >= date_since:
                        card_type = 'NOSPECS' if card_name.strip().lower() == 'nospecs' else 'ALINEACION'
                        alignments.append({
                            'serial': serial,
                            'date': alignment_date,
                            'date_altus': altus_date,
                            'vehicle': " ".join(item for item in card_vehicle_data if isinstance(item, str)),
                            'url': f'{URL_OPENAPI}/{card_hash}',
                            'type': card_type
                        })
                        keep_fetching = False
                        break
                    if (altus_date - date_since).days < -1:
                        keep_fetching = False

                except ValueError:
                    error_logger.exception(
                        f"Error al procesar fecha '{altus_date}' de tarjeta {card_hash}")

            if keep_fetching:
                page_number += 1

            access_logger.info(f'Last date: {altus_date}')

        except requests.exceptions.HTTPError as http_err:
            error_logger.exception(f"Error HTTP: {http_err}")
            error_logger.exception(
                "El servidor respondió con un error. Deteniendo.")
            keep_fetching = False
        except requests.exceptions.ConnectionError as conn_err:
            error_logger.exception(f"Error de Conexión: {conn_err}")
            error_logger.exception(
                f"No se pudo conectar a '{URL_FOR_REQUEST}'. ¿Está el servidor encendido?")
            keep_fetching = False
        except requests.exceptions.Timeout:
            error_logger.exception(
                "Error: La petición (timeout) de 10 segundos fue superada.")
            keep_fetching = False
        except requests.exceptions.RequestException as err:
            error_logger.exception(
                f"Ocurrió un error inesperado en la petición: {err}")
            keep_fetching = False

    alignments_to_send = []
    for alignment in alignments:
        if not r.exists(alignment.get('serial')):
            alignments_to_send.append(alignment)

    return alignments_to_send


def main(date_since: datetime, date_until: datetime) -> None:
    '''Main execution'''

    alignments = get_altus_data(date_since, date_until)
    data = get_vehicles_data(alignments)
    send_mail(data, MAIL_RECIPIENTS.split(' '))
