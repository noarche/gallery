import os
import time
from PIL import Image

# Directory paths
gallery_root = './galleryRoot/'
thumbs_dir = './thumbs/'

# HTML Template
html_template = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <link rel="icon" href="favicon.ico" type="image/x-icon">
    <title>{title}</title>
    <style>
        body {{
            background-color: #161616;
            color: #ececec;
            font-family: Tahoma, sans-serif;
            margin: 18px;
        }}
        .gallery {{
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(160px, 1fr));
            gap: 8px;
        }}
        .gallery img {{
            width: 100%;
            height: auto;
            border: 2px solid #444;
            border-radius: 8px;
        }}
        .gallery-info {{
            text-align: center;
            margin-top: 18px;
        }}
        footer {{
            text-align: center;
            margin-top: 28px;
            color: #5e5e5e;
        }}
        a {{
            color: #1db954;
            text-decoration: none;
        }}
        a:hover {{
            color: #1db954;
            text-decoration: underline;
        }}
    </style>
</head>
<body>
    <h1>{title}</h1>
    <div class="gallery">
        {thumbnails}
    </div>
    <div class="gallery-info">
        <p>Total Images: {total_images}</p>
        <p>Gallery Size: {gallery_size}</p>
    </div>
    <footer>
        Latest Update: {last_updated}
    </footer>
</body>
</html>
'''

def human_readable_size(size):
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if size < 1024:
            return f"{size:.2f} {unit}"
        size /= 1024
    return f"{size:.2f} TB"

def get_directory_size(directory):
    total_size = 0
    for dirpath, _, filenames in os.walk(directory):
        for f in filenames:
            fp = os.path.join(dirpath, f)
            total_size += os.path.getsize(fp)
    return total_size

def get_gallery_data():
    gallery_data = {}
    for dir_name in os.listdir(gallery_root):
        dir_path = os.path.join(gallery_root, dir_name)
        if os.path.isdir(dir_path):
            images = [f for f in os.listdir(dir_path) if f.lower().endswith(('.png', '.jpg', '.jpeg', '.webp'))]
            images.sort(key=lambda x: os.path.getmtime(os.path.join(dir_path, x)), reverse=True)
            gallery_data[dir_name] = images
    return gallery_data

def create_thumbnail(image_path, thumb_path, size=(160, 160)):
    try:
        with Image.open(image_path) as img:
            img.thumbnail(size)
            img.save(thumb_path, "webp", quality=77)
    except Exception as e:
        print(f"Error creating thumbnail for {image_path}: {e}")

def create_thumbnails(image_paths, gallery_dir):
    thumbnails_html = ""
    
    for img_file in image_paths:
        img_path = os.path.join(gallery_dir, img_file)

        # Ensure thumbnail directory exists
        if not os.path.exists(thumbs_dir):
            os.makedirs(thumbs_dir)

        # Path to store the thumbnail
        thumb_file = f"{os.path.splitext(img_file)[0]}_thumb.jpg"
        thumb_path = os.path.join(thumbs_dir, thumb_file)

        # Create the thumbnail if it doesn't exist
        if not os.path.exists(thumb_path):
            create_thumbnail(img_path, thumb_path)

        # Reference the thumbnail in the HTML
        thumbnails_html += f'<a href="{img_path}"><img src="{thumb_path}" alt="{img_file}"></a>\n'
    
    return thumbnails_html

def create_gallery_page(gallery_name, images):
    gallery_dir = os.path.join(gallery_root, gallery_name)

    # Create thumbnails and generate HTML
    thumbnails_html = create_thumbnails(images, gallery_dir)

    total_images = len(images)
    gallery_size = human_readable_size(get_directory_size(gallery_dir))
    last_updated = time.strftime('%A %B %d %Y %H:%M')

    html_content = html_template.format(
        title=gallery_name,
        thumbnails=thumbnails_html,
        total_images=total_images,
        gallery_size=gallery_size,
        last_updated=last_updated
    )

    # Write the HTML content to a file beside index.html
    with open(f"{gallery_name}.html", 'w', encoding='utf-8') as f:
        f.write(html_content)

def create_index_page(gallery_data):
    thumbnails_html = ""
    total_images = 0
    total_size = 0

    for gallery_name, images in gallery_data.items():
        if images:
            latest_image = images[0]
            total_images += len(images)
            total_size += get_directory_size(os.path.join(gallery_root, gallery_name))

            # Reference the most recent image thumbnail
            gallery_dir = os.path.join(gallery_root, gallery_name)
            thumb_file = f"{os.path.splitext(latest_image)[0]}_thumb.jpg"
            thumbnail = os.path.join(thumbs_dir, thumb_file)

            # Link to the individual gallery pages
            thumbnails_html += f'<a href="./{gallery_name}.html"><img src="{thumbnail}" alt="{gallery_name}"></a>\n'

    last_updated = time.strftime('%A %B %d %Y %H:%M')
    gallery_size = human_readable_size(total_size)

    index_html_content = html_template.format(
        title="Gallery Albums",
        thumbnails=thumbnails_html,
        total_images=total_images,
        gallery_size=gallery_size,
        last_updated=last_updated
    )

    # Write the HTML content to the index.html file in the root directory
    with open("index.html", 'w', encoding='utf-8') as f:
        f.write(index_html_content)

def main():
    gallery_data = get_gallery_data()

    # Create individual gallery pages
    for gallery_name, images in gallery_data.items():
        create_gallery_page(gallery_name, images)

    # Create index page
    create_index_page(gallery_data)

if __name__ == "__main__":
    main()

