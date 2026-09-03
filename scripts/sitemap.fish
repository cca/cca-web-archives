#!/usr/bin/env fish
# Do 3 things for sitemap.xml files in archived static sites:
# 1. write URLs CSV for Internet Archive
# 2. Copy to sitemap.original.xml
# 3. Point sitemap.xml URLs to gh pages
set root_dir $argv[1]
# assume dir name = domain of the site
set domain (basename $root_dir)
cd $root_dir || begin
    set_color --bold red
    echo -e "Failed to change directory to \"$root_dir\"\nAre you sure it exists?"
    set_color normal
    exit 1
end

if ! test -f "sitemap.xml"
    set_color --bold red
    echo -e "No sitemap.xml found in the \"$root_dir\" directory"
    set_color normal
    echo "See if it exists at https://$domain/sitemap.xml and download it if so"
    exit 1
end

grep -oP '(?<=<loc>).*?(?=</loc>)' sitemap.xml | sort > ~/Downloads/$domain.csv
cp sitemap.xml sitemap.original.xml
sed -i '' "s|https://$domain|https://cca.github.io/$domain|g" sitemap.xml
