from pathlib import Path
import argparse
import tempfile
import tarfile
import logging
import shutil


def unity_extract_package(
	package_path: Path | str,
	output_dir: Path | str = None,
	*,
	include_meta: bool = True,
	overwrite: bool = False,
) -> None:
	# Package file
	package_path: Path = Path(package_path)
	assert package_path.exists() and package_path.is_file(), "File does not exist or is not a file."

	# Create output dir
	if output_dir is None:
		output_dir: Path = package_path.with_name(package_path.stem)
		output_dir.mkdir(exist_ok=overwrite)
	else:
		output_dir: Path = Path(output_dir)
		output_dir.mkdir(exist_ok=True)

	with tempfile.TemporaryDirectory() as temp_dir:
		temp_dir: Path = Path(temp_dir)
		logging.debug(f"Created temp dir at {temp_dir}")
		extract_location: Path = temp_dir / "Contents"

		# Extract package contents to temp directory
		with tarfile.open(package_path, 'r') as package:
			logging.info(f"Extracting package to {extract_location.resolve()}")
			package.extractall(extract_location)
			logging.debug(f"Extracted package to {extract_location.resolve()}")

		# Copy files structurally to output directory
		for asset_parent_dir in extract_location.glob("*"):
			with open(asset_parent_dir / "pathname", 'rb') as f:
				# Path in output folder
				asset_dest_path: str = str(f.read(), encoding="utf8").strip()
				asset_dest_path: Path = output_dir / asset_dest_path
				asset_dest_path.parent.mkdir(exist_ok=True, parents=True)

				# Path in temp folder
				asset_src_path: Path = asset_parent_dir / "asset"

				if not asset_src_path.exists():
					continue

				if asset_dest_path.exists():
					continue

				shutil.copy(asset_src_path, asset_dest_path)
				logging.debug(f"Copied asset to {asset_dest_path.resolve()}")
				if include_meta:
					meta_dest_path: Path = asset_dest_path.with_name(asset_dest_path.name + ".meta")
					shutil.copy(asset_parent_dir / "asset.meta", meta_dest_path)
					logging.debug(f"Copied meta to {meta_dest_path.resolve()}")


def main():
	parser = argparse.ArgumentParser(description="Extract a `.unitypackage` file.")
	parser.add_argument("-i", metavar="PATH", type=Path, help="Path to unitypackage file.", required=True)
	parser.add_argument("--no-meta", action="store_true", help="Exclude meta files.")
	parser.add_argument("--overwrite", "-W", action="store_true", help="Allow writing output to existing directory. Always True if custom output directory is given.")
	parser.add_argument("--output", "-o", metavar="PATH", type=Path, help="Directory to copy files into.")
	args = parser.parse_args()

	logging.basicConfig(format="%(asctime)s - %(levelname)s: %(message)s", datefmt='%Y-%m-%d %H:%M:%S', level=logging.DEBUG)

	unity_extract_package(
		package_path=args.i.resolve(),
		output_dir=args.output,
		include_meta=not args.no_meta,
		overwrite=args.overwrite
	)


if __name__ == "__main__":
	main()
