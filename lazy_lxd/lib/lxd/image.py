from lib import inquirer


def exists(self) -> bool:
    """
    Search local lxc image by os and its release

    Returns:
        bool: True image exists. False if not.
    """

    all_images = self._client.images.all()
    for image in all_images:
        if _search_image(self.image_os, self.image_version, image) is not None:
            return True
    return False


def get_fingerprint(self) -> list:
    """
    Get images list properties by image search os and and it version.

    Returns:
        list: List of dicts contains image properties, uploaded datetime and fingerprint.
    """

    images = self._client.images.all()
    images_properties = list()

    for image in images:
        if _search_image(self.image_os, self.image_version, image) is not None:
            pass
            properties = image.properties
            properties.update({
                'uploaded_at': image.uploaded_at,
                'fingerprint': image.fingerprint
            })
            images_properties.append(properties)

    if len(images_properties) > 1:
        self._log.warning("Found more than one requested image.")
        return _choose_image(images_properties)
    else:
        return images_properties[0]['fingerprint']


def _search_image(os: str, codename: str, image: object) -> object:
    """
    Internal function for compare image properties such as os and codename
    with search criteria.

    Args:
        os (str): Operating system name
        codename (str): OS codename, like xenial for Ubuntu 16.04 Xenial Xerus
        image (object): image object from lxd api
    Returns:
        object: lxd image object, which fits the search criteria
    """

    props = image.properties
    if props['os'].lower() == os and props['release'].lower() == codename:
        return image


def _choose_image(images: list) -> str:
    """
    Ask user what image he want use from many found images.
    Build human readable string with information about each image.

    Args:
        images (list): LXC images list.

    Returns:
        str: Fingerprint of chosen image.
    """

    import dateutil.parser
    from datetime import datetime
    import humanize

    images_list = list()
    for image in images:
        # convert uploaded_at to relative days
        uploaded_time = dateutil.parser.isoparse(image['uploaded_at'])
        time_diff = datetime.now() - uploaded_time.replace(tzinfo=None)
        uploaded_diff = humanize.naturaldelta(time_diff)

        image_representation = (
            f"OS - {image['os'].capitalize()} | "
            f"Release - {image['release'].capitalize()} | "
            f"Architecture - {image['architecture']} | Uploaded - {uploaded_diff} ago"
        )
        images_list.append(image_representation)

    chosed_image_index = inquirer.choose(images_list)

    return images[chosed_image_index]['fingerprint']


def download(self) -> None:
    """
    Downloading LXD image from linuxcontainers.org to local storage.
    """

    from halo import Halo

    try:
        with Halo(text="Loading image...", spinner="dots12", color="blue"):
            self._client.images.create_from_simplestreams(
                'https://images.linuxcontainers.org',
                f'{self.image_os}/{self.image_version}',
                auto_update=True
            )
    except Exception as e:
        raise e
