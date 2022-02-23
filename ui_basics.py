import streamlit as st


def mk_para(form):
    form.text("jai shri krishna ")


def mk_radio(form):
    form.radio(label="choose yes no", options=["yes", "no"])


def mk_button(form):
    form.form_submit_button(label="Submit now")


if __name__ == '__main__':

    st.title("Title")
    st.header("This is header")
    st.subheader("This is Subheader")

    st.text("Sample text for the website.Sample text for the website.Sample text for the website.")
    st.text("Sample text for the website.Sample text for the website. Sample text for the website.")
    st.markdown("This is markdown text")

    st.success("Success!!")
    st.warning("Warning!!")
    st.info("Information")
    st.error("Error!!")

    st.write("Text with write")
    st.write(range(5))

    form = st.form("form1")
    mk_para(form)
    mk_radio(form)
    mk_button(form)

    from PIL import Image

    img = Image.open("streamlit.png")
    st.image(img, width=200)

    if st.checkbox("Show/Hide"):
        st.text("showing the widget")

    st.checkbox("Check 1")
    st.checkbox("Check 2")

    status = st.radio("Select option", ('Yes', 'No'))

    if status == 'Yes':
        st.success("Success")
    else:
        st.error("Failure")

    hobby = st.selectbox("Hobbies :", ['Reading', 'Biking', 'Dancing'])
    st.write("Your hobby is:", hobby)

    hobbies = st.multiselect("Hobbies :", ['Reading', 'Biking', 'Dancing'])
    st.write("You selected :", len(hobbies),hobbies)

    st.button("Click me")

    if st.button("Submit"):
        st.text("Form submitted!")

