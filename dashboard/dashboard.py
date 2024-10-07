import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import seaborn as sns
import streamlit as st
from func import DataAnalyzer
from babel.numbers import format_currency
import urllib

@st.cache_data
def load_data():
    main_data = pd.read_csv("https://raw.githubusercontent.com/VincenImanuell/Tugas_Dicoding_Analisis_Data/refs/heads/main/dashboard/main_data.csv")
    geolocation_data = pd.read_csv("https://raw.githubusercontent.com/VincenImanuell/Tugas_Dicoding_Analisis_Data/refs/heads/main/dashboard/geolocation.csv")
    return main_data, geolocation_data

main_data, geolocation_data = load_data()

def prepare_data(main_data):
    total_pembelian_produk = main_data.groupby("product_category_name_english")["product_id"].count().reset_index()
    total_pembelian_produk = total_pembelian_produk.rename(columns={"product_id": "products"})
    total_pembelian_produk = total_pembelian_produk.sort_values(by="products", ascending=False)
    return total_pembelian_produk

sum_order_items_df = prepare_data(main_data)

function = DataAnalyzer(main_data)
st.title("Dashboard E-Commerce")

# Produk paling banyak terjual
st.subheader("Jenis produk yang paling banyak terjual")
top_products = sum_order_items_df.head(5)

# Normalisasi warna
norm = plt.Normalize(sum_order_items_df['products'].min(), sum_order_items_df['products'].max())
cmap = plt.get_cmap('Blues')

# Mendapatkan warna berdasarkan jumlah produk
colors = cmap(norm(sum_order_items_df['products'].values))  # Mendapatkan warna
colors = colors[:, :3].tolist()  # Mengambil RGB dan mengonversi ke list

fig_top, ax_top = plt.subplots(figsize=(12, 6))
sns.barplot(x="products", y="product_category_name_english", data=top_products, palette=colors, ax=ax_top)
ax_top.set_ylabel("Kategori Produk", fontsize=15)
ax_top.set_xlabel("Jumlah Produk Terjual", fontsize=15)
ax_top.set_title("Jenis Produk yang Paling Banyak Terjual", loc="center", fontsize=18)
ax_top.tick_params(axis='y', labelsize=15)
st.pyplot(fig_top)

with st.expander("Lihat Penjelasan"):
    st.write('Berdasarkan visualisasi data di atas, maka kategori produk yang paling banyak terjual adalah bed_bath_table.')

# Produk paling sedikit terjual
st.subheader("Jenis produk yang paling sedikit terjual")

norm = plt.Normalize(sum_order_items_df['products'].min(), sum_order_items_df['products'].max())
cmap = plt.get_cmap('Blues_r')

# Mendapatkan warna berdasarkan jumlah produk
colors = cmap(norm(sum_order_items_df['products'].values))  # Mendapatkan warna
colors = (colors[:, :3]*0.9).tolist()  # Mengambil RGB dan mengonversi ke list

bottom_products = sum_order_items_df.sort_values(by="products", ascending=True).head(5)

fig_top, ax_top = plt.subplots(figsize=(12, 6))
sns.barplot(x="products", y="product_category_name_english", data=bottom_products, palette=colors, ax=ax_top)
ax_top.set_ylabel("Kategori Produk", fontsize=15)
ax_top.set_xlabel("Jumlah Produk Terjual", fontsize=15)
ax_top.set_title("Jenis Produk yang Paling Sedikit Terjual", loc="center", fontsize=18)
ax_top.tick_params(axis='y', labelsize=15)
st.pyplot(fig_top)

with st.expander("Lihat Penjelasan"):
    st.write('Berdasarkan visualisasi data di atas, maka kategori produk yang paling sedikit terjual adalah security_and_services.')

# Pengaruh harga pada jumlah penjualan produk
category_sales = main_data.groupby('product_category_name_english')['order_item_id'].count().reset_index()
category_sales = category_sales.rename(columns={'order_item_id': 'total_sold'})

# Menghitung harga rata-rata per kategori barang
average_price = main_data.groupby('product_category_name_english')['price'].mean().reset_index()

# Merge data total sold dan average price
combined_data = category_sales.merge(average_price, on='product_category_name_english')

# Ambil 15 kategori teratas
top_15_categories = combined_data.nlargest(15, 'total_sold')

# Fungsi untuk menampilkan garis tepi / spines pada plot
def custom_plot(ax, spines):
    for loc, spine in ax.spines.items():
        if loc in spines:
            spine.set_position(('outward', 10))  # Spines bottom dan left dipindahkan ke luar
        else:
            spine.set_color('none')  # Spines yang tidak ditentukan dihilangkan
    ax.xaxis.set_ticks_position('bottom')
    ax.yaxis.set_ticks_position('left')

# Membuat plot
def plot_categories(data):
    fig, ax = plt.subplots(figsize=(12, 8))
    custom_plot(ax, ['bottom', 'left'])

    hb = ax.scatter(x=data['product_category_name_english'],  # Sumbu x: Kategori barang
                     y=data['total_sold'],                  # Sumbu y: Jumlah terjual
                     c=data['price'],                       # Warna titik: Harga rata-rata
                     cmap='viridis',                        # Menggunakan colormap 'viridis'
                     s=data['total_sold'] * 0.75,         # Ukuran titik berdasarkan jumlah terjual
                     alpha=0.7,                            # Transparansi titik
                     edgecolor='w')                        # Warna tepi titik

    plt.xticks(rotation=45, ha='right')  # Memutar label sumbu x 45 derajat agar mudah dibaca
    plt.title('15 Kategori Barang Terlaris', fontsize=16)  # Judul plot
    plt.xlabel('Kategori Barang', fontsize=12)  # Label sumbu x
    plt.ylabel('Jumlah Terjual', fontsize=12)    # Label sumbu y

    # Menambahkan colorbar untuk menunjukkan harga rata-rata
    cbar = plt.colorbar(hb, ax=ax)
    cbar.set_label('Harga Rata-rata', rotation=270, labelpad=20, fontsize=12)

    plt.tight_layout()
    st.pyplot(fig)  # Menampilkan plot di Streamlit

# Menampilkan judul dan penjelasan
st.subheader("Pengaruh harga barang pada jumlah penjualan barang")
st.write("Berikut adalah plot yang menunjukkan 10 kategori barang terlaris berdasarkan jumlah terjual.")

# Panggil fungsi plot
plot_categories(top_15_categories)

with st.expander("Lihat Penjelasan"):
    st.write('Ternyata, harga produk memiliki pengaruh terhadap banyaknya penjualan, karena kategori barang yang penjualannya paling banyak cenderung memiliki harga barang yang rendah. (ditunjukkan dengan warna pada dot scatter plot)')

# Persebaran lokasi customer
def plot_brazil_map(data):
    brazil = mpimg.imread(urllib.request.urlopen('https://raw.githubusercontent.com/VincenImanuell/Tugas_Dicoding_Analisis_Data/refs/heads/main/dashboard/brazil_map.jpg'),'jpg')
    fig_map, ax_map = plt.subplots(figsize=(10, 10))
    data.plot(kind="scatter", x="geolocation_lng", y="geolocation_lat", ax=ax_map, alpha=0.3, s=0.3, c='blue')
    plt.axis('off')
    plt.imshow(brazil, extent=[-73.98283055, -33.8, -33.75116944, 5.4])
    st.pyplot(fig_map)

st.subheader("Lokasi customer dengan visualisasi menggunakan peta")
plot_brazil_map(geolocation_data)

with st.expander("Lihat Penjelasan"):
    st.write('Berdasarkan visualisasi data dengan peta di atas, ada lebih banyak pelanggan di bagian tenggara. Ada lebih banyak pelanggan di kota-kota besar seperti Sao Paulo, Rio de Janeiro, Rio Grande do Sul, dan Parana.')

data_kota = pd.read_csv("https://raw.githubusercontent.com/VincenImanuell/Tugas_Dicoding_Analisis_Data/refs/heads/main/data/customers_dataset.csv")

jumlah_customer = data_kota.groupby("customer_city")["customer_id"].count().reset_index()

jumlah_customer = jumlah_customer.rename(columns={"customer_id": "jumlah"})

jumlah_customer = jumlah_customer.sort_values(by="jumlah", ascending=False)

# Menghitung warna berdasarkan jumlah customer
norm = plt.Normalize(jumlah_customer['jumlah'].min(), jumlah_customer['jumlah'].max())
cmap = plt.get_cmap('Blues')  # Mengambil colormap biru

# Mendapatkan warna berdasarkan jumlah customer
colors = cmap(norm(jumlah_customer['jumlah']))  # Mendapatkan warna
colors = (colors[:, :3]*0.8).tolist()  # Mengambil RGB dan mengonversi ke list

fig_top, ax_top = plt.subplots(figsize=(12, 6))
# Membuat bar plot menggunakan seaborn
sns.barplot(x="jumlah", y="customer_city", 
            data=jumlah_customer.head(10), palette=colors, ax=ax_top)

# Membuat label sumbu x dan y
ax_top.set_ylabel("Nama Kota", fontsize=15)
ax_top.set_xlabel("Jumlah Customer", fontsize=15)

# Mengatur judul
plt.gca().set_title("Persebaran Customer Pada Tiap Kota", loc="center", fontsize=18)

ax_top.set_title("Persebaran Customer Pada Tiap Kota", loc="center", fontsize=18)
ax_top.tick_params(axis='y', labelsize=15)
st.pyplot(fig_top)

st.caption('Copyright (C) Vincen Imanuel 2024')

with st.sidebar:
    st.image("https://github.com/dicodingacademy/assets/raw/main/logo.png")