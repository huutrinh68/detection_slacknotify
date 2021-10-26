import io
import cv2
import requests
from time import sleep

# slack notify setting
SLACK_URL = 'https://slack.com/api/files.upload'
# @TODO change this value
CHANNEL_ID = 'C02KL7D9GN5'
# @TODO change this value
SLACK_TOKEN = 'xoxb-2644784446804-2643559509221-HTx9IPn3SuBNUTEoQvvZOpxx'


def image_diff(before_image_gray, current_image_gray):
    diff = cv2.absdiff(before_image_gray, current_image_gray)
    _, diff_binary = cv2.threshold(diff, 50, 255, cv2.THRESH_BINARY)
    sum_diff = cv2.countNonZero(diff_binary)
    thresh = before_image_gray.shape[0] * before_image_gray.shape[1] * 0.1
    print('image_shape: {}'.format(before_image_gray.shape))
    print('sum_diff: {}'.format(sum_diff))
    print('thresh: {}'.format(thresh))
    if sum_diff < thresh:
        return False
    return True


def Interval():
    cap = cv2.VideoCapture(0)
    before_image_origin = None
    before_image_gray = None
    while True:
        try:
            _, current_image_origin = cap.read()
            if current_image_origin is None:
                sleep(1)
                continue
            # calculate a differrence between a previous image and a current image
            save_im = False
            current_image_gray = cv2.cvtColor(current_image_origin, cv2.COLOR_BGR2GRAY)
            if before_image_gray is None:
                before_image_gray = current_image_gray
                before_image_origin = current_image_origin
            else:
                save_im = image_diff(before_image_gray, current_image_gray)
                print(save_im)
                if save_im:
                    cv2.putText(before_image_origin,
                                text='before',
                                org=(20, 50),
                                fontFace=cv2.FONT_HERSHEY_SIMPLEX,
                                fontScale=1.0,
                                color=(0, 255, 0),
                                thickness=2,
                                lineType=cv2.LINE_4)
                    cv2.putText(current_image_origin,
                                text='after',
                                org=(20, 50),
                                fontFace=cv2.FONT_HERSHEY_SIMPLEX,
                                fontScale=1.0,
                                color=(0, 255, 0),
                                thickness=2,
                                lineType=cv2.LINE_4)
                    hconcat = cv2.hconcat([before_image_origin, current_image_origin])

                    # slack notify
                    if SLACK_TOKEN and CHANNEL_ID:
                        try:
                            encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), 100]
                            _, encoded_image = cv2.imencode('.jpeg', hconcat, encode_param)

                            files = {
                                'file': io.BytesIO(encoded_image)
                            }
                            param = {
                                'token': SLACK_TOKEN,
                                'channels': CHANNEL_ID,
                                'filename': "detected.jpeg",
                                'initial_comment': "Detected!",
                                'title': "image"
                            }

                            response = requests.post(SLACK_URL, params=param, files=files)
                            print(response)
                            sleep(60)
                        except Exception as e:
                            print('Could not send image to Slack: {}'.format(e))

                before_image_gray = current_image_gray
                before_image_origin = current_image_origin

            cv2.imshow("Frame", current_image_origin)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
            sleep(1)
        except Exception as e:
            print(e)
            sleep(60)


def main():
    Interval()


if __name__ == '__main__':
    main()
