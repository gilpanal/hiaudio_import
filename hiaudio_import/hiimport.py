import argparse
import coloredlogs, logging
import glob, os

import requests
from urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)

log = logging.getLogger(__name__)
coloredlogs.install(level='DEBUG', logger=log, fmt="%(asctime)s [%(name)s:%(threadName)s] %(levelname)s: %(message)s")


ENDPOINT = ""

TOKEN = ""
AUTH_HEADER = {"Authorization": ""}

def main():

    parser = argparse.ArgumentParser(description="An import script for hiaudio.fr")

    parser.add_argument('--loglevel', dest='LOG_LEVEL', type=lambda s : s.upper(),
                    choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'], default="INFO",
                    help='Global log level')

    parser.add_argument("--endpoint", type=str, help="the endpoint location of the platform", required=False, default="https://hiaudio.fr")
    parser.add_argument("--token-var", type=str, help="the environment variable containing the JWT for API requests", default="JWT")


    parser.add_argument("--dataset-path", type=str, help="the main folder containing the dataset", required=True)
    parser.add_argument("--parent-collection", type=str, help="an option collection name for everything that will be imported", required=False, default=None)

    parser.add_argument("--collections-pattern", type=str, help='the pattern to find collections folders, relative to dataset root [default: no collections]', required=False, default="")
    parser.add_argument("--compositions-pattern", type=str, help='the pattern to find compositions [default: %%(collection_path)s/*]', required=False, default='%(collection_path)s/*')
    parser.add_argument("--tracks-pattern", type=str, help='the pattern to find tracks [default:  %%(composition_path)s/*]', required=False, default='%(composition_path)s/*')

    args = parser.parse_args()

    log.setLevel(getattr(logging, args.LOG_LEVEL))

    log.debug(args)

    global ENDPOINT
    ENDPOINT = args.endpoint
    log.debug(f"HiAudio enpoint set to {args.endpoint}")



    TOKEN = os.environ.get(args.token_var)
    AUTH_HEADER['Authorization'] = "Bearer " + TOKEN
    log.debug(f"Auth header set to {AUTH_HEADER}")


    parentcol_id = None
    if args.parent_collection:
        pok, parentcol_id = create_collection(args.parent_collection)
        if pok:
            log.info(f"Created parent collection {args.parent_collection}")


    collections_pattern = args.collections_pattern
    log.debug("Collections pattern: " + collections_pattern)


    all_collections = glob.glob(collections_pattern, root_dir=args.dataset_path ) if collections_pattern != "" else ["."]
    log.debug(f"All collections: {all_collections}")


    nb_cols = nb_comps = nb_tracks = 0

    for col_idx, collection_path in enumerate(all_collections, start=1):

        collection_name = os.path.basename(collection_path) if collection_path != "." else ""

        col_ok, col_uuid = True, parentcol_id

        if collection_name:
            log.info(f"[{col_idx}/{len(all_collections)}] Found collection '{collection_name}' at {collection_path}")

            col_ok, col_uuid = create_collection(collection_name, parent_id=parentcol_id)

            nb_cols += 1 if col_ok else 0

        if col_ok:

            compositions_pattern = args.compositions_pattern % locals()
            all_compositions = glob.glob(compositions_pattern, root_dir=args.dataset_path )

            log.debug(f"Compositions pattern '{compositions_pattern}' -> files {all_compositions}")

            for comp_idx, composition_path in enumerate(all_compositions, start=1):

                composition_name = os.path.basename(composition_path)

                log.info(f"\t[{comp_idx}/{len(all_compositions)}] Found composition {composition_name}")

                comp_ok, comp_uuid = create_composition(composition_name, collection_id=col_uuid)

                if comp_ok:

                    nb_comps += 1

                    tracks_pattern = args.tracks_pattern % locals()
                    all_tracks = glob.glob(tracks_pattern, root_dir=args.dataset_path )

                    log.debug(f"Tracks pattern '{tracks_pattern}' -> files {all_tracks}")

                    for tr_idx, track_path in enumerate(all_tracks, start=1):

                        track_name = os.path.basename(track_path)

                        log.info(f"\t\t[{tr_idx}/{len(all_tracks)}] Adding track: {track_name}")

                        tr_ok = create_track(comp_uuid, os.path.join(args.dataset_path, track_path))

                        if tr_ok: nb_tracks += 1


    log.info(f"Imported {nb_cols} collections, {nb_comps} compositions, {nb_tracks} tracks.")




def create_collection(name, parent_id=None, priv=3):

    method = "/newcollection"

    data = {
        'title': name,
        'privacy_level': priv
    }

    if parent_id:
        data["parent_uuid"] = parent_id

    r = requests.post(ENDPOINT + method, json=data, headers=AUTH_HEADER, verify=False)

    log.debug(f"create_collection() responded: {r}")

    ok, uid = False, None

    if 200 <= r.status_code < 300:
        r = r.json()

        ok = r.get("ok", False)
        uid = r.get("uuid", None)

    if not ok:
        log.error(f"Error on create_collection({name}, {priv}): {r}")

    return (ok, uid)


def create_composition(name, collection_id=None, priv=3):
    method = "/newcomposition"

    data = {
        'title': name,
        'privacy_level': priv
    }

    if collection_id:
        data['parent_uuid'] = collection_id

    r = requests.post(ENDPOINT + method, json=data, headers=AUTH_HEADER, verify=False)

    log.debug(f"create_composition() responded: {r}")

    ok, uid = False, None

    if 200 <= r.status_code < 300:
        r = r.json()

        ok = r.get("ok", False)
        if ok:
            uid = r["composition"]["uuid"]

    if not ok:
        log.error(f"Error on create_composition({name}, {collection_id}, {priv}): {r}")

    return (ok, uid)



def create_track(composition_id, trackfile_path):

    if not os.path.isfile(trackfile_path):
        log.error(f"Track file {trackfile_path} does not exist")

    method = "/fileUpload"

    data = {
        'composition_id': composition_id
    }
    files = {
        'audio' : (os.path.basename(trackfile_path), open(trackfile_path, 'rb')),

    }

    r = requests.post(ENDPOINT + method, data=data, files=files, headers=AUTH_HEADER, verify=False)
    # r = requests.post(ENDPOINT + method, data=data, headers=AUTH_HEADER, verify=False)
    # r = requests.post(ENDPOINT + method, files=files, headers=AUTH_HEADER, verify=False)

    # req = requests.Request('POST','http://stackoverflow.com',headers={'X-Custom':'Test'},data='a=1&b=2')
    # req = requests.Request('POST',ENDPOINT + method, data=data, headers=AUTH_HEADER)

    # prepared = req.prepare()
    # pretty_print_POST(prepared)

    # s = requests.Session()
    # s.verify=False
    # r = s.send(prepared)

    log.debug(f"create_track() responded: {r}")

    ok = False

    if 200 <= r.status_code < 300:
        r = r.json()

        ok = r.get("ok", False)

    if not ok:
        log.error(f"Error on create_track({composition_id}, {trackfile_path}): {r}")

    return ok




def pretty_print_POST(req):
    """
    At this point it is completely built and ready
    to be fired; it is "prepared".

    However pay attention at the formatting used in
    this function because it is programmed to be pretty
    printed and may differ from the actual request.
    """
    print('{}\n{}\r\n{}\r\n\r\n{}'.format(
        '-----------START-----------',
        req.method + ' ' + req.url,
        '\r\n'.join('{}: {}'.format(k, v) for k, v in req.headers.items()),
        req.body,
    ))




if __name__ == "__main__":
    main()
