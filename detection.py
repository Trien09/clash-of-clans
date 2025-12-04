import aircv as ac


def locate_image(screenshot, reference_array, threshold):
    for reference in reference_array:
        try:
            result = ac.find_template(screenshot, ac.imread(f"images/{reference}"), threshold)
            if result:
                return result['result'][:2]
        except Exception as e:
            # Print error for debugging
            print(f"Error loading image {reference}: {e}")
            continue
    return None