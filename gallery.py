import os
import time
from PIL import Image

# Directory paths
gallery_root = './galleryRoot/'
thumbs_dir = './thumbs/'
template_path = './src/template.html'

def load_template():
    """Load the HTML template from the specified file."""
    try:
        with open(template_path, 'r', encoding='utf-8') as template_file:
            return template_file.read()
    except FileNotFoundError:
        print(f"Error: Template file {template_path} not found.")
        return ''

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

def create_thumbnail(image_path, thumb_path, size=(150, 150)):
    try:
        with Image.open(image_path) as img:
            img.thumbnail(size)

            # Ensure thumbnail directory exists
            if not os.path.exists(os.path.dirname(thumb_path)):
                os.makedirs(os.path.dirname(thumb_path))
            
            # Save thumbnail in the same format as the original file
            img.save(thumb_path, img.format, quality=95)
    except Exception as e:
        print(f"Error creating thumbnail for {image_path}: {e}")

def create_thumbnails(image_paths, gallery_dir):
    thumbnails_html = ""
    
    for img_file in image_paths:
        img_path = os.path.join(gallery_dir, img_file)

        # Path to store the thumbnail (same format as original)
        thumb_file = f"{os.path.splitext(img_file)[0]}_thumb.{img_file.split('.')[-1]}"
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

    html_template = load_template()

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
            thumb_file = f"{os.path.splitext(latest_image)[0]}_thumb.{latest_image.split('.')[-1]}"
            thumbnail = os.path.join(thumbs_dir, thumb_file)

            # Link to the individual gallery pages
            thumbnails_html += f'<a href="./{gallery_name}.html"><img src="{thumbnail}" alt="{gallery_name}"></a>\n'

    last_updated = time.strftime('%A %B %d %Y %H:%M')
    gallery_size = human_readable_size(total_size)

    html_template = load_template()

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

