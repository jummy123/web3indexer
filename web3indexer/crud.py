import structlog

from pymongo.database import Database

from .models import Contract, Nft, UpsertOwnership, Transfer
from .utils import get_nft_id, get_transfer_id


log = structlog.get_logger()


def insert_if_not_exists(db: Database, address, abi):
    contract = db.nft_contracts.find_one({"address": address})
    if contract is None:
        db.nft_contracts.insert_one(
            {
                "address": address,
                "abi": abi,
            }
        )


def insert_event(db: Database, address, event):
    """
    Insert an event into mongodb
    """
    contract_id = db.nft_contracts.find_one({"address": address})["_id"]
    db.nft_events.insert_one(
        {
            "address": address,
            "name": event["event"],
            "event": event,
            "blockNumber": event["blockNumber"],
            "tokenId": event["args"].get("tokenId"),
        }
    )


def get_last_scanned_event(db: Database, address, default=9000000):
    """
    Return the block number the last event
    was added at.
    """
    event = db.nft_events.find_one(
        {"$query": {"address": address}, "$orderby": {"blockNumber": -1}},
    )
    # Inneficient XXX
    if event is None:
        return default
    return event["blockNumber"]


def get_contract(db: Database, address):
    return db.contracts.find_one({"_id": address})


def upsert_contract(db: Database, contract: Contract):
    """
    Insert a contract into mongodb
    """
    db.contracts.find_one_and_update(
        {"_id": contract.address},
        {"$set": contract.dict(by_alias=True)},
        upsert=True,
    )


def get_nft(db: Database, contract_address: str, token_id: int):
    return db.nfts.find_one({"_id": "{}-{}".format(contract_address, token_id)})


def upsert_nft(db: Database, nft: Nft):
    nft_id = get_nft_id(nft.contract_id, nft.token_id)
    db.nfts.find_one_and_update(
        {"_id": nft_id},
        {"$set": {**nft.dict()}},
        upsert=True,
    )


def upsert_ownership(db: Database, upsert_ownership: UpsertOwnership):
    # TODO: Need to check if `block_number` and `log_index` have already
    # been processed to ensure we don't update unnecessarily
    db.ownerships.find_one_and_update(
        {
            "nft_id": upsert_ownership.nft_id,
            "owner": upsert_ownership.owner,
        },
        {
            "$set": {
                "nft_id": upsert_ownership.nft_id,
                "owner": upsert_ownership.owner,
            },
            "$inc": {"quantity": upsert_ownership.delta_quantity},
        },
        upsert=True,
    )


def upsert_transfer(db: Database, transfer: Transfer):
    """
    Insert a transfer event into mongodb
    """
    db.transfers.find_one_and_update(
        {"_id": get_transfer_id(transfer)},
        {"$set": transfer.dict(by_alias=True)},
        upsert=True,
    )


def get_all_contracts(db):
    return db.nft_contracts.find({}, {"address": 1, "abi": 1, "_id": 0})
