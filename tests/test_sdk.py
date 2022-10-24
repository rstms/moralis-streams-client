# moralis sdk tests

from logging import info

import MoralisSDK.api
from box import Box


def test_api_moralis_sdk(moralis, system_address, user_address):
    info(f"{system_address=}")
    system_nfts = Box(moralis.get_nfts(system_address, chain="goerli"))
    for nft in system_nfts.result:
        info(
            f"{nft.symbol} {int(nft.token_id)} {nft.name} mint_block={nft.block_number_minted} contract={nft.token_address}"
        )

    info(f"{user_address=}")
    user_nfts = Box(moralis.get_nfts(user_address, chain="goerli"))
    for nft in user_nfts.result:
        info(
            f"{nft.symbol} {int(nft.token_id)} {nft.name} mint_block={nft.block_number_minted} contract={nft.token_address}"
        )
